"""
Flask API for Saga Orchestrator.
Provides HTTP endpoints to trigger saga orchestrations.
"""
from flask import Flask, request, jsonify
from saga_orchestrator.tasks import orchestrate_registration_saga
import uuid
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'saga_orchestrator'}), 200


@app.route('/saga/register', methods=['POST'])
def trigger_registration_saga():
    """
    Trigger User Registration Saga.
    
    Request Body:
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    
    Returns:
    {
        "saga_id": "uuid",
        "status": "pending|success|failed",
        "task_id": "celery_task_id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        saga_id = str(uuid.uuid4())
        
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'password': data['password']
        }
        
        task = orchestrate_registration_saga.apply_async(
            args=[saga_id, user_data],
            task_id=f'saga_{saga_id}'
        )
        
        logger.info(f"Registration saga triggered: saga_id={saga_id}, task_id={task.id}")
        
        return jsonify({
            'saga_id': saga_id,
            'status': 'pending',
            'task_id': task.id,
            'message': 'Registration saga started'
        }), 202
        
    except Exception as e:
        logger.error(f"Error triggering saga: {str(e)}")
        return jsonify({'error': f'Failed to trigger saga: {str(e)}'}), 500


@app.route('/saga/status/<task_id>', methods=['GET'])
def get_saga_status(task_id):
    """
    Get the status and result of a saga execution.
    
    Args:
        task_id: Celery task ID
        
    Returns:
    {
        "task_id": "string",
        "status": "PENDING|SUCCESS|FAILURE",
        "result": {...} (if completed)
    }
    """
    try:
        from saga_orchestrator.celery_app import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'task_id': task_id,
                'status': 'PENDING',
                'message': 'Task is still processing'
            }
        elif task.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'status': 'SUCCESS',
                'result': task.result
            }
        elif task.state == 'FAILURE':
            response = {
                'task_id': task_id,
                'status': 'FAILURE',
                'error': str(task.info) if task.info else 'Task failed'
            }
        else:
            response = {
                'task_id': task_id,
                'status': task.state,
                'result': task.result if task.ready() else None
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting saga status: {str(e)}")
        return jsonify({'error': f'Failed to get saga status: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)