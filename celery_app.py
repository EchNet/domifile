from celery import Celery

celery = Celery("main")
celery.config_from_object("config")
