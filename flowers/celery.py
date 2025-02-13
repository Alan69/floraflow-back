from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowers.settings')

app = Celery('flowers')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-store-ratings-daily': {
        'task': 'stores.tasks.update_store_ratings',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight (00:00)
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
