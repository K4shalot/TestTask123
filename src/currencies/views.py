from django.utils.dateparse import parse_datetime
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Currency, RateSnapshot, TrackedCurrency
from .serializers import (
    AddTrackedCurrencySerializer,
    AvailableCurrencySerializer,
    CurrencyHistorySerializer,
    LatestRateFieldsMixin,
    TrackedCurrencySerializer,
    UpdateMonitoringSerializer,
)


class TrackedCurrencyListView(generics.ListAPIView, LatestRateFieldsMixin):
    serializer_class = TrackedCurrencySerializer

    def get_queryset(self):
        qs = TrackedCurrency.objects.select_related("currency")
        return self.with_latest_rate(qs)


class AvailableCurrenciesView(generics.ListAPIView):
    serializer_class = AvailableCurrencySerializer

    def get_queryset(self):
        return Currency.objects.exclude(tracking__isnull=False).order_by("code")


class AddTrackedCurrencyView(generics.CreateAPIView):
    serializer_class = AddTrackedCurrencySerializer

    @extend_schema(
        responses={201: TrackedCurrencySerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tracked = serializer.save()
        tracked_with_rate = LatestRateFieldsMixin.with_latest_rate(
            TrackedCurrency.objects.select_related("currency").filter(pk=tracked.pk)
        ).first()
        output = TrackedCurrencySerializer(tracked_with_rate)
        return Response(output.data, status=status.HTTP_201_CREATED)


class CurrencyHistoryView(generics.ListAPIView):
    serializer_class = CurrencyHistorySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="start", type=str, required=True, description="ISO datetime"),
            OpenApiParameter(name="end", type=str, required=True, description="ISO datetime"),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        code = self.kwargs["code"]
        start = parse_datetime(self.request.query_params.get("start", ""))
        end = parse_datetime(self.request.query_params.get("end", ""))
        if not start or not end:
            raise ValidationError(
                {"detail": "Both 'start' and 'end' ISO datetime query params are required."}
            )
        if start > end:
            raise ValidationError({"detail": "'start' must be less than or equal to 'end'."})
        return RateSnapshot.objects.filter(
            currency__code=code,
            source_timestamp__gte=start,
            source_timestamp__lte=end,
        ).order_by("source_timestamp")


class ToggleMonitoringView(APIView):
    def patch(self, request, pk):
        tracked = generics.get_object_or_404(TrackedCurrency, pk=pk)
        serializer = UpdateMonitoringSerializer(tracked, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        tracked_with_rate = LatestRateFieldsMixin.with_latest_rate(
            TrackedCurrency.objects.select_related("currency").filter(pk=tracked.pk)
        ).first()
        output = TrackedCurrencySerializer(tracked_with_rate)
        return Response(output.data)
