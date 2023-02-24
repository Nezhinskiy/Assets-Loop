import logging
from datetime import datetime, timezone, timedelta

from django.shortcuts import redirect
from django.views.generic import ListView

from core.models import InfoLoop
from core.tasks import assets_loop,  all_reg, assets_loop_stop
from django_filters.views import FilterView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from arbitration.settings import \
    INTER_EXCHANGES_OBSOLETE_IN_MINUTES
from core.filters import ExchangesFilter
from core.serializers import InterExchangesSerializer
from crypto_exchanges.models import InterExchanges
from arbitration.celery import app

logger = logging.getLogger(__name__)

def registration(request):
    all_reg.s().delay()
    if not InfoLoop.objects.all():
        InfoLoop.objects.create(value=False)
    return redirect('core:info')


def start(request):
    if InfoLoop.objects.first().value == 0:
        InfoLoop.objects.create(value=True)
        assets_loop.s().delay()
    return redirect('core:inter_exchanges_list_new')


def stop(request):
    if InfoLoop.objects.first().value == 1:
        assets_loop_stop.s().delay()
    return redirect('core:info')


class InfoLoopList(ListView):
    model = InfoLoop
    template_name = 'crypto_exchanges/info.html'

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(InfoLoopList, self).get_context_data(**kwargs)
        context['info_loops'] = self.get_queryset()
        context['loops_count'] = self.get_queryset().count
        return context


class InterExchangesListNew(FilterView):
    model = InterExchanges
    template_name = 'crypto_exchanges/new.html'
    filterset_class = ExchangesFilter


class InterExchangesAPIView(ListAPIView, FilterView):
    model = InterExchanges
    serializer_class = InterExchangesSerializer
    filterset_class = ExchangesFilter

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
            queryset = queryset.order_by(ordering)
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
