import os
from celery import Celery
from celery.schedules import crontab



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyStoreV2.settings')
app = Celery('MyStore', broker_connection_retry=False,
             broker_connection_retry_on_startup=True, )
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()
app.conf.beat_schedule = {
    'send-email-to-subscribers-every-sunday-at-12-00': {
        'task': 'apps.accounts.tasks.send_email_to_subscribers',
        'schedule': crontab(minute=0, hour=12, day_of_week='sunday'),
    },
}
