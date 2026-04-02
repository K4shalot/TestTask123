import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db.models import OuterRef, Subquery

from currencies.models import RateSnapshot, TrackedCurrency


class Command(BaseCommand):
    help = "Export currently tracked currencies with latest rates to CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="currency_rates.csv",
            help="Output CSV file path.",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"]).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        latest_rate_qs = RateSnapshot.objects.filter(currency=OuterRef("currency")).order_by("-source_timestamp", "-id")
        queryset = TrackedCurrency.objects.select_related("currency").annotate(
            latest_rate_buy=Subquery(latest_rate_qs.values("rate_buy")[:1]),
            latest_rate_sell=Subquery(latest_rate_qs.values("rate_sell")[:1]),
            latest_rate_cross=Subquery(latest_rate_qs.values("rate_cross")[:1]),
            latest_rate_time=Subquery(latest_rate_qs.values("source_timestamp")[:1]),
        )

        rows_written = 0
        try:
            with output_path.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(
                    [
                        "code",
                        "code_alpha",
                        "is_enabled",
                        "rate_buy",
                        "rate_sell",
                        "rate_cross",
                        "rate_time",
                    ]
                )
                for tracked in queryset:
                    writer.writerow(
                        [
                            tracked.currency.code,
                            tracked.currency.code_alpha,
                            tracked.is_enabled,
                            tracked.latest_rate_buy,
                            tracked.latest_rate_sell,
                            tracked.latest_rate_cross,
                            tracked.latest_rate_time.isoformat() if tracked.latest_rate_time else "",
                        ]
                    )
                    rows_written += 1
        except OSError as exc:
            raise CommandError(f"Failed to write CSV file: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(f"CSV exported to {output_path} ({rows_written} rows)")
        )
