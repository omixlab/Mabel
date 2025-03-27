MAKEFLAGS := -j2

build:
	@docker compose --env-file .env build

run:
	@docker compose --env-file .env up

webserver_locally:
	FLASK_APP=src/__init__.py flask run --host=0.0.0.0 --port=8099

worker_locally:
	celery -A src.utils.extractor.celery worker -n MABEL_WORKER -E

all_locally: webserver_locally worker_locally
