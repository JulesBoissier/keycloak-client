web: gunicorn app:server --workers 4
worker: celery -A periodic_tasks:celery_app worker --loglevel=INFO