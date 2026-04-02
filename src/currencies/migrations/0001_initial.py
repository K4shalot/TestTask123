from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Currency",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.PositiveIntegerField(unique=True)),
                ("code_alpha", models.CharField(blank=True, max_length=3)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("code",),
            },
        ),
        migrations.CreateModel(
            name="RateSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rate_buy", models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ("rate_sell", models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ("rate_cross", models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ("source_timestamp", models.DateTimeField()),
                ("fetched_at", models.DateTimeField(auto_now_add=True)),
                (
                    "currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rate_snapshots",
                        to="currencies.currency",
                    ),
                ),
            ],
            options={
                "ordering": ("-source_timestamp", "-id"),
                "indexes": [models.Index(fields=["currency", "source_timestamp"], name="currencies__currenc_c8218b_idx")],
            },
        ),
        migrations.CreateModel(
            name="TrackedCurrency",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "currency",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tracking",
                        to="currencies.currency",
                    ),
                ),
            ],
            options={
                "ordering": ("currency__code",),
            },
        ),
    ]
