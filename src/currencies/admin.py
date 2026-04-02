from django.contrib import admin

from .models import Currency, RateSnapshot, TrackedCurrency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "code_alpha", "created_at")
    search_fields = ("code", "code_alpha")


@admin.register(TrackedCurrency)
class TrackedCurrencyAdmin(admin.ModelAdmin):
    list_display = ("id", "currency", "is_enabled", "created_at")
    list_filter = ("is_enabled",)
    search_fields = ("currency__code", "currency__code_alpha")


@admin.register(RateSnapshot)
class RateSnapshotAdmin(admin.ModelAdmin):
    list_display = ("id", "currency", "rate_buy", "rate_sell", "rate_cross", "source_timestamp")
    search_fields = ("currency__code", "currency__code_alpha")
    list_filter = ("currency",)
