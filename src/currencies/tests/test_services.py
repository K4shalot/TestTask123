from datetime import datetime, timezone
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from currencies.services import _normalize_uah_pair, fetch_monobank_uah_pairs


class NormalizeUahPairTests(SimpleTestCase):
    def test_returns_none_for_non_uah_pair(self):
        row = {
            "currencyCodeA": 840,
            "currencyCodeB": 978,
            "date": 1710000000,
            "rateBuy": 1.0,
            "rateSell": 1.1,
        }

        self.assertIsNone(_normalize_uah_pair(row))

    def test_extracts_target_currency_and_timestamp(self):
        row = {
            "currencyCodeA": 840,
            "currencyCodeB": 980,
            "date": 1710000000,
            "rateBuy": 39.5,
            "rateSell": 40.2,
            "rateCross": None,
        }

        result = _normalize_uah_pair(row)

        self.assertIsNotNone(result)
        self.assertEqual(result["code"], 840)
        self.assertEqual(result["rate_buy"], 39.5)
        self.assertEqual(result["rate_sell"], 40.2)
        self.assertIsNone(result["rate_cross"])
        self.assertEqual(
            result["source_timestamp"],
            datetime.fromtimestamp(1710000000, tz=timezone.utc),
        )


class FetchMonobankPairsTests(SimpleTestCase):
    @patch("currencies.services.requests.get")
    def test_fetch_filters_to_uah_pairs_only(self, mock_get):
        payload = [
            {
                "currencyCodeA": 840,
                "currencyCodeB": 980,
                "date": 1710000000,
                "rateBuy": 39.5,
                "rateSell": 40.2,
            },
            {
                "currencyCodeA": 978,
                "currencyCodeB": 980,
                "date": 1710000300,
                "rateBuy": 42.1,
                "rateSell": 42.8,
            },
            {
                "currencyCodeA": 840,
                "currencyCodeB": 978,
                "date": 1710000600,
                "rateBuy": 0.9,
                "rateSell": 1.0,
            },
        ]
        response = Mock()
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        result = fetch_monobank_uah_pairs()

        self.assertEqual(len(result), 2)
        self.assertEqual([row["code"] for row in result], [840, 978])
        mock_get.assert_called_once_with("https://api.monobank.ua/bank/currency", timeout=15)
