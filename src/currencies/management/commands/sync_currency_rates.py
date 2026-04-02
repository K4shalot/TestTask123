from django.core.management.base import BaseCommand

from currencies.services import sync_currency_rates


class Command(BaseCommand):
    help = "Fetch latest rates from Monobank API and save them."

    def handle(self, *args, **options):
        saved_count = sync_currency_rates()
        self.stdout.write(self.style.SUCCESS(f"Saved {saved_count} currency snapshots."))
