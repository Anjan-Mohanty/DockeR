from celery import Celery

celery_app = Celery(
    'app',
    broker='amqp://myuser_pp:mypassword_pp@rabbitmqpreprocess:5673'
)

