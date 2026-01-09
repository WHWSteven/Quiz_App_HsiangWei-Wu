"""
API routes for Quiz Service.
These endpoints are used by the Saga Orchestrator.
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import UserProfile, Category
import logging

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'quiz_service'}), 200


@api_bp.route('/users/profile', methods=['POST'])
def create_user_profile():
    """
    Create user profile in Quiz Service.
    This endpoint is called by the Saga Orchestrator as Step 2 of registration.
    
    Request Body:
    {
        "user_id": int,
        "default_preferences": {
            "notifications_enabled": bool,
            "default_category": int (optional)
        }
    }
    
    Returns:
    {
        "id": int,
        "user_id": int,
        "notifications_enabled": bool,
        "default_category_id": int or null,
        "created_at": string
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Check if profile already exists
        existing_profile = UserProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            return jsonify({
                'error': f'Profile for user_id {user_id} already exists',
                'profile': existing_profile.to_dict()
            }), 400
        
        # Extract preferences
        preferences = data.get('default_preferences', {})
        notifications_enabled = preferences.get('notifications_enabled', True)
        default_category_id = preferences.get('default_category')
        
        # Validate category if provided
        if default_category_id:
            category = Category.query.get(default_category_id)
            if not category:
                return jsonify({'error': f'Category {default_category_id} does not exist'}), 400
        
        # Create user profile
        profile = UserProfile(
            user_id=user_id,
            notifications_enabled=notifications_enabled,
            default_category_id=default_category_id
        )
        
        db.session.add(profile)
        db.session.commit()
        
        logger.info(f"User profile created for user_id: {user_id}")
        
        return jsonify(profile.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating user profile: {str(e)}")
        return jsonify({'error': f'Failed to create user profile: {str(e)}'}), 500


@api_bp.route('/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    """
    Get user profile by user_id.
    
    Args:
        user_id: The user ID to get profile for
        
    Returns:
        User profile dictionary or 404 if not found
    """
    try:
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({'error': f'Profile for user_id {user_id} not found'}), 404
        
        return jsonify(profile.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({'error': f'Failed to get user profile: {str(e)}'}), 500


@api_bp.route('/users/<int:user_id>/profile/compensate', methods=['DELETE'])
def compensate_delete_profile(user_id):
    """
    Compensation endpoint for Saga pattern.
    Deletes a user profile as part of a saga rollback operation.
    This is called when a saga needs to compensate (rollback) profile creation.
    
    Args:
        user_id: The user ID whose profile should be deleted
        
    Returns:
        Success message
    """
    try:
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            # Profile doesn't exist - this is ok for compensation (idempotent)
            return jsonify({
                'success': True,
                'message': f'Profile for user_id {user_id} does not exist (already deleted or never created)',
                'compensated': True
            }), 200
        
        profile_id = profile.id
        db.session.delete(profile)
        db.session.commit()
        
        logger.info(f"User profile deleted for compensation: user_id={user_id}, profile_id={profile_id}")
        
        return jsonify({
            'success': True,
            'message': f'Profile for user_id {user_id} has been deleted for compensation',
            'user_id': user_id,
            'profile_id': profile_id,
            'compensated': True
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error compensating (deleting profile): {str(e)}")
        return jsonify({
            'error': f'Failed to compensate (delete profile): {str(e)}',
            'user_id': user_id
        }), 500