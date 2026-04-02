import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "sync-currency-rates-every-10-minutes": {
        "task": "currencies.tasks.sync_currency_rates",
        "schedule": crontab(minute="*/10"),
    }
}
