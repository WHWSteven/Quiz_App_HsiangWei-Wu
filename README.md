# Quiz App with Saga Pattern

## Requirements
- Python 3.11
- Node.js 18+
- Redis running on localhost:6379

## Setup

### Backend
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


Start Services (separate terminals)
# Redis
redis-server

# User Service
cd user_service
python app.py

# Quiz Service
cd quiz_service
python app.py

# Saga Orchestrator
python -m saga_orchestrator.run_orchestrator

# Celery Worker
python -m celery -A saga_orchestrator.celery_app worker --loglevel=info --pool=solo

#Gateway
cd gateway
npm install
npm start
