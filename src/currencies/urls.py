from django.urls import path

from .views import (
    AddTrackedCurrencyView,
    AvailableCurrenciesView,
    CurrencyHistoryView,
    ToggleMonitoringView,
    TrackedCurrencyListView,
)

urlpatterns = [
    path("currencies/tracked/", TrackedCurrencyListView.as_view(), name="tracked-currencies"),
    path("currencies/available/", AvailableCurrenciesView.as_view(), name="available-currencies"),
    path("currencies/tracked/add/", AddTrackedCurrencyView.as_view(), name="add-tracked-currency"),
    path("currencies/<int:code>/history/", CurrencyHistoryView.as_view(), name="currency-history"),
    path("currencies/tracked/<int:pk>/monitoring/", ToggleMonitoringView.as_view(), name="toggle-monitoring"),
]
