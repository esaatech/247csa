from celery import shared_task

@shared_task
def example_task():
    return "Hello from Celery!"