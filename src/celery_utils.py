from celery import Celery
import os


def make_celery(app):
    app.config["CELERY_BROKER_URL"] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')
    app.config["CELERY_RESULT_BACKEND"] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

    celery = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
