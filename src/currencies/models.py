from django.db import models


class Currency(models.Model):
    code = models.PositiveIntegerField(unique=True)
    code_alpha = models.CharField(max_length=3, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:
        return self.code_alpha or str(self.code)


class TrackedCurrency(models.Model):
    currency = models.OneToOneField(
        Currency,
        on_delete=models.CASCADE,
        related_name="tracking",
    )
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("currency__code",)

    def __str__(self) -> str:
        return f"{self.currency} ({'enabled' if self.is_enabled else 'disabled'})"


class RateSnapshot(models.Model):
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="rate_snapshots",
    )
    rate_buy = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    rate_sell = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    rate_cross = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    source_timestamp = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-source_timestamp", "-id")
        indexes = [
            models.Index(fields=("currency", "source_timestamp")),
        ]

    def __str__(self) -> str:
        return f"{self.currency} @ {self.source_timestamp.isoformat()}"
