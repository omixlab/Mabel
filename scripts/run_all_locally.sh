source .env

FLASK_APP=src/__init__.py flask run --host=0.0.0.0 --port=5001 && celery -A src.utils.extractor.celery worker
