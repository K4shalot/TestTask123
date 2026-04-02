from django.db.models import OuterRef, Subquery
from rest_framework import serializers

from .models import Currency, RateSnapshot, TrackedCurrency


class LatestRateFieldsMixin:
    @staticmethod
    def with_latest_rate(queryset):
        latest_rate_qs = RateSnapshot.objects.filter(currency=OuterRef("currency")).order_by("-source_timestamp", "-id")
        return queryset.annotate(
            latest_rate_buy=Subquery(latest_rate_qs.values("rate_buy")[:1]),
            latest_rate_sell=Subquery(latest_rate_qs.values("rate_sell")[:1]),
            latest_rate_cross=Subquery(latest_rate_qs.values("rate_cross")[:1]),
            latest_rate_time=Subquery(latest_rate_qs.values("source_timestamp")[:1]),
        )


class TrackedCurrencySerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(source="currency.code", read_only=True)
    code_alpha = serializers.CharField(source="currency.code_alpha", read_only=True)
    latest_rate_buy = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True, read_only=True)
    latest_rate_sell = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True, read_only=True)
    latest_rate_cross = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True, read_only=True)
    latest_rate_time = serializers.DateTimeField(allow_null=True, read_only=True)

    class Meta:
        model = TrackedCurrency
        fields = (
            "id",
            "code",
            "code_alpha",
            "is_enabled",
            "latest_rate_buy",
            "latest_rate_sell",
            "latest_rate_cross",
            "latest_rate_time",
        )


class AvailableCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ("id", "code", "code_alpha")


class AddTrackedCurrencySerializer(serializers.Serializer):
    code = serializers.IntegerField(min_value=1)

    def validate_code(self, value: int) -> int:
        if not Currency.objects.filter(code=value).exists():
            raise serializers.ValidationError("Currency code is not available yet. Sync rates first.")
        if TrackedCurrency.objects.filter(currency__code=value).exists():
            raise serializers.ValidationError("Currency is already tracked.")
        return value

    def create(self, validated_data):
        currency = Currency.objects.get(code=validated_data["code"])
        return TrackedCurrency.objects.create(currency=currency)


class UpdateMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackedCurrency
        fields = ("is_enabled",)


class CurrencyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RateSnapshot
        fields = ("source_timestamp", "rate_buy", "rate_sell", "rate_cross")
