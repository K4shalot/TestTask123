from celery import shared_task

from . import services


@shared_task(
    autoretry_for=(services.RetryableSyncError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def sync_currency_rates() -> int:
    return services.sync_currency_rates()
