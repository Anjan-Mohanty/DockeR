from celery import Celery

celery_app = Celery(
    'app',
    broker='amqp://myuser:mypassword@rabbitmq:5672'
)

