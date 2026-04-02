from celery import shared_task

from .services import sync_currency_rates as sync_currency_rates_service


@shared_task
def sync_currency_rates() -> int:
    return sync_currency_rates_service()
