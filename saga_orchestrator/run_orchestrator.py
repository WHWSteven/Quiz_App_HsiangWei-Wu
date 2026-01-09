
from saga_orchestrator.api import app

if __name__ == '__main__':
    print("Starting Saga Orchestrator API on http://localhost:5002")
    print("Make sure Redis is running on localhost:6379")
    print("Make sure Celery worker is running (use: celery -A saga_orchestrator.celery_app worker --loglevel=info)")
    app.run(debug=True, port=5002)