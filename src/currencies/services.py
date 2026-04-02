from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import requests
from django.db import transaction

from .models import Currency, RateSnapshot

MONOBANK_CURRENCY_URL = "https://api.monobank.ua/bank/currency"
UAH_CODE = 980

ISO_NUMERIC_TO_ALPHA = {
    840: "USD",
    978: "EUR",
    985: "PLN",
    826: "GBP",
    203: "CZK",
    756: "CHF",
    124: "CAD",
    392: "JPY",
}


def _normalize_uah_pair(raw_row: dict[str, Any]) -> dict[str, Any] | None:
    code_a = raw_row.get("currencyCodeA")
    code_b = raw_row.get("currencyCodeB")
    if code_a != UAH_CODE and code_b != UAH_CODE:
        return None
    target_code = code_a if code_b == UAH_CODE else code_b
    timestamp = datetime.fromtimestamp(raw_row["date"], tz=timezone.utc)
    return {
        "code": target_code,
        "rate_buy": raw_row.get("rateBuy"),
        "rate_sell": raw_row.get("rateSell"),
        "rate_cross": raw_row.get("rateCross"),
        "source_timestamp": timestamp,
    }


def fetch_monobank_uah_pairs(timeout: int = 15) -> list[dict[str, Any]]:
    response = requests.get(MONOBANK_CURRENCY_URL, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    rows: list[dict[str, Any]] = []
    for raw_row in payload:
        normalized = _normalize_uah_pair(raw_row)
        if normalized is not None:
            rows.append(normalized)
    return rows


@transaction.atomic
def sync_currency_rates() -> int:
    rows = fetch_monobank_uah_pairs()
    snapshots: list[RateSnapshot] = []
    for row in rows:
        code = row["code"]
        currency, _ = Currency.objects.get_or_create(
            code=code,
            defaults={"code_alpha": ISO_NUMERIC_TO_ALPHA.get(code, "")},
        )
        snapshots.append(
            RateSnapshot(
                currency=currency,
                rate_buy=Decimal(str(row["rate_buy"])) if row["rate_buy"] is not None else None,
                rate_sell=Decimal(str(row["rate_sell"])) if row["rate_sell"] is not None else None,
                rate_cross=Decimal(str(row["rate_cross"])) if row["rate_cross"] is not None else None,
                source_timestamp=row["source_timestamp"],
            )
        )
    if snapshots:
        RateSnapshot.objects.bulk_create(snapshots)
    return len(snapshots)
