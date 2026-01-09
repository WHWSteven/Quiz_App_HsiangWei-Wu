"""
Saga Orchestrator Tasks using Celery.

This module implements the Orchestration approach of the Saga Design Pattern.
The orchestrator coordinates multiple service operations and handles compensation
(rollback) if any step fails.
"""
import requests
import logging
from celery import chain, group
from saga_orchestrator.celery_app import celery_app
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
USER_SERVICE_URL = 'http://127.0.0.1:5001'
QUIZ_SERVICE_URL = 'http://127.0.0.1:5000'

# Saga state keys in Redis
SAGA_STATE_PREFIX = 'saga_state:'


class SagaError(Exception):
    pass


@celery_app.task(bind=True, name='saga.create_user')
def create_user_task(self, saga_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    
    try:
        logger.info(f"[Saga {saga_id}] Step 1: Creating user in User Service")
        
        response = requests.post(
            f'{USER_SERVICE_URL}/users',
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 201:
            user = response.json()
            user_id = user.get('id')
            
            logger.info(f"[Saga {saga_id}] Step 1 SUCCESS: User created with ID {user_id}")
            
            state = {
                'step': 'create_user',
                'status': 'completed',
                'user_id': user_id,
                'user_data': user
            }
            
            return {
                'success': True,
                'user_id': user_id,
                'user_data': user,
                'compensation_data': {'user_id': user_id}  
            }
        else:
            error_msg = response.json().get('error', 'Unknown error')
            logger.error(f"[Saga {saga_id}] Step 1 FAILED: {error_msg}")
            raise SagaError(f"Failed to create user: {error_msg}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"[Saga {saga_id}] Step 1 ERROR: {str(e)}")
        raise SagaError(f"User service communication error: {str(e)}")
    except Exception as e:
        logger.error(f"[Saga {saga_id}] Step 1 EXCEPTION: {str(e)}")
        raise SagaError(f"Unexpected error in create_user: {str(e)}")


@celery_app.task(bind=True, name='saga.create_user_profile')
def create_user_profile_task(self, saga_id: str, step1_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 2: Create user profile in Quiz Service.
    This depends on Step 1 completing successfully.
    
    Args:
        saga_id: Unique identifier for this saga instance
        step1_result: Result from create_user_task containing user_id
        
    Returns:
        Dictionary with profile creation result
    """
    try:
        user_id = step1_result.get('user_id')
        if not user_id:
            raise SagaError("Missing user_id from previous step")
            
        logger.info(f"[Saga {saga_id}] Step 2: Creating user profile in Quiz Service for user {user_id}")
        
        profile_data = {
            'user_id': user_id,
            'default_preferences': {
                'notifications_enabled': True,
                'default_category': None
            }
        }
        
        response = requests.post(
            f'{QUIZ_SERVICE_URL}/api/users/profile',
            json=profile_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            profile = response.json()
            logger.info(f"[Saga {saga_id}] Step 2 SUCCESS: User profile created")
            
            return {
                'success': True,
                'profile': profile,
                'compensation_data': {'user_id': user_id}  # Data needed for rollback
            }
        else:
            error_msg = response.json().get('error', 'Unknown error')
            logger.error(f"[Saga {saga_id}] Step 2 FAILED: {error_msg}")
            raise SagaError(f"Failed to create user profile: {error_msg}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"[Saga {saga_id}] Step 2 ERROR: {str(e)}")
        raise SagaError(f"Quiz service communication error: {str(e)}")
    except Exception as e:
        logger.error(f"[Saga {saga_id}] Step 2 EXCEPTION: {str(e)}")
        raise SagaError(f"Unexpected error in create_user_profile: {str(e)}")


@celery_app.task(bind=True, name='saga.compensate_delete_user')
def compensate_delete_user_task(self, saga_id: str, compensation_data: Dict[str, Any]) -> Dict[str, Any]:
    
    try:
        user_id = compensation_data.get('user_id')
        if not user_id:
            logger.warning(f"[Saga {saga_id}] COMPENSATE: No user_id provided, skipping")
            return {'success': True, 'skipped': True}
            
        logger.info(f"[Saga {saga_id}] COMPENSATE: Deleting user {user_id} from User Service")
        
        response = requests.delete(
            f'{USER_SERVICE_URL}/users/{user_id}/compensate',
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"[Saga {saga_id}] COMPENSATE SUCCESS: User {user_id} deleted")
            return {'success': True, 'user_id': user_id}
        else:
            error_msg = response.json().get('error', 'Unknown error')
            logger.error(f"[Saga {saga_id}] COMPENSATE FAILED: {error_msg}")
            # Note: We log but don't raise - compensation failures should be logged but not block
            return {'success': False, 'error': error_msg}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"[Saga {saga_id}] COMPENSATE ERROR: {str(e)}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        logger.error(f"[Saga {saga_id}] COMPENSATE EXCEPTION: {str(e)}")
        return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, name='saga.compensate_delete_profile')
def compensate_delete_profile_task(self, saga_id: str, compensation_data: Dict[str, Any]) -> Dict[str, Any]:
    
    try:
        user_id = compensation_data.get('user_id')
        if not user_id:
            logger.warning(f"[Saga {saga_id}] COMPENSATE: No user_id provided, skipping")
            return {'success': True, 'skipped': True}
            
        logger.info(f"[Saga {saga_id}] COMPENSATE: Deleting user profile {user_id} from Quiz Service")
        
        response = requests.delete(
            f'{QUIZ_SERVICE_URL}/api/users/{user_id}/profile/compensate',
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"[Saga {saga_id}] COMPENSATE SUCCESS: Profile {user_id} deleted")
            return {'success': True, 'user_id': user_id}
        else:
            # Profile might not exist, which is ok for compensation
            logger.warning(f"[Saga {saga_id}] COMPENSATE: Profile deletion returned {response.status_code}")
            return {'success': True, 'note': 'Profile may not have existed'}
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"[Saga {saga_id}] COMPENSATE ERROR: {str(e)}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        logger.warning(f"[Saga {saga_id}] COMPENSATE EXCEPTION: {str(e)}")
        return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, name='saga.orchestrate_registration')
def orchestrate_registration_saga(self, saga_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    
    try:
        logger.info(f"[Saga {saga_id}] Starting Registration Saga Orchestration")
        
        # Execute Step 1: Create User
        step1_result = create_user_task.apply(args=[saga_id, user_data])
        
        if not step1_result.successful() or not step1_result.result.get('success'):
            error = step1_result.result if isinstance(step1_result.result, dict) else {'error': 'Step 1 failed'}
            logger.error(f"[Saga {saga_id}] Step 1 failed: {error}")
            return {
                'success': False,
                'saga_id': saga_id,
                'failed_step': 1,
                'error': error.get('error', 'User creation failed')
            }
        
        step1_data = step1_result.result
        logger.info(f"[Saga {saga_id}] Step 1 completed successfully")
        
        # Execute Step 2: Create User Profile
        step2_result = create_user_profile_task.apply(args=[saga_id, step1_data])
        
        if not step2_result.successful() or not step2_result.result.get('success'):
            # Step 2 failed - need to compensate Step 1
            logger.error(f"[Saga {saga_id}] Step 2 failed, initiating compensation")
            
            compensation_result = compensate_delete_user_task.apply(
                args=[saga_id, step1_data.get('compensation_data', {})]
            )
            
            error = step2_result.result if isinstance(step2_result.result, dict) else {'error': 'Step 2 failed'}
            
            return {
                'success': False,
                'saga_id': saga_id,
                'failed_step': 2,
                'error': error.get('error', 'Profile creation failed'),
                'compensation': {
                    'executed': True,
                    'result': compensation_result.result if compensation_result.successful() else None
                }
            }
        
        # Both steps succeeded
        logger.info(f"[Saga {saga_id}] All saga steps completed successfully")
        
        return {
            'success': True,
            'saga_id': saga_id,
            'result': {
                'user': step1_data.get('user_data'),
                'profile': step2_result.result.get('profile')
            }
        }
        
    except Exception as e:
        logger.error(f"[Saga {saga_id}] Saga orchestration exception: {str(e)}")
        # Try to compensate if we have user_id
        try:
            if 'step1_data' in locals() and step1_data:
                compensate_delete_user_task.apply(
                    args=[saga_id, step1_data.get('compensation_data', {})]
                )
        except:
            pass  # Best effort compensation
            
        return {
            'success': False,
            'saga_id': saga_id,
            'error': f'Saga orchestration failed: {str(e)}'
        }