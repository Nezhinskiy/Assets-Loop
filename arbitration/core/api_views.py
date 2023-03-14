from datetime import datetime, timedelta, timezone

from django_filters.views import FilterView
from rest_framework import throttling
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from arbitration.settings import INTER_EXCHANGES_OBSOLETE_IN_MINUTES
from core.filters import ExchangesFilter
from core.serializers import InterExchangesSerializer
from crypto_exchanges.models import InterExchanges


class InterExchangesAPIView(ListAPIView, FilterView):
    """
    View returns a list of serialized InterExchanges objects in JSON format,
    which can be used to display exchange information in a web application.
    It also filters the list based on user search queries using the same
    ExchangesFilter. It uses a ListAPIView, and provides pagination and
    ordering capabilities for the data using a custom list method. It also
    implements rate limiting using the throttle_classes attribute.
    """
    model = InterExchanges
    serializer_class = InterExchangesSerializer
    filterset_class = ExchangesFilter
    throttle_classes = (throttling.AnonRateThrottle,)

    def get_queryset(self):
        qs = self.model.objects.prefetch_related(
            'input_bank', 'output_bank', 'bank_exchange',
            'input_crypto_exchange', 'output_crypto_exchange',
            'interim_crypto_exchange', 'second_interim_crypto_exchange',
            'update'
        ).filter(
            update__updated__gte=(
                datetime.now(timezone.utc) - timedelta(
                    minutes=INTER_EXCHANGES_OBSOLETE_IN_MINUTES
                )
            )
        )
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        return self.filter.qs

    def filter_for_datatable(self, queryset):
        # ordering
        ordering_column = self.request.query_params.get('order[0][column]')
        ordering_direction = self.request.query_params.get('order[0][dir]')
        ordering = None
        if ordering_column == '0':
            ordering = 'diagram'
        if ordering_column == '1':
            ordering = 'marginality_percentage'
        if ordering and ordering_direction == 'desc':
            ordering = f"-{ordering}"
        if ordering:
            return queryset.order_by(ordering)
        return queryset

    def list(self, request, *args, **kwargs):
        draw = request.query_params.get('draw')
        queryset = self.get_queryset()
        records_total = queryset.count()
        filtered_queryset = self.filter_for_datatable(queryset)
        try:
            start = int(request.query_params.get('start'))
        except ValueError:
            start = 0
        try:
            length = int(request.query_params.get('length'))
        except ValueError:
            length = 10
        if length not in [10, 25, 50, 100]:
            length = 10
        end = length + start
        serializer = self.get_serializer(filtered_queryset[start:end],
                                         many=True)
        response = {
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': filtered_queryset.count(),
            'data': serializer.data
        }
        return Response(response)
