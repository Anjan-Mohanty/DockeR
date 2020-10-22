from celery import Celery

celery_app = Celery(
    'app',
    broker='amqp://myuser_dc:mypassword_dc@rabbitmqdiscovercontent:5693'
)
