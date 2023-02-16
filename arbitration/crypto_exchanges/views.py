from datetime import datetime, time, timedelta, timezone

from django.contrib.postgres.search import SearchVector
from django.db.models import Count, F, Prefetch
from django.http import Http404
from django.views.generic import ListView
from django_filters.views import FilterView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from banks.banks_config import BANKS_CONFIG
from banks.models import Banks
from core.models import InfoLoop
from crypto_exchanges.crypto_exchanges_registration.binance import (
    TinkoffBinanceP2PParser, WiseBinanceP2PParser,
    get_all_binance_crypto_exchanges, get_all_card_2_wallet_2_crypto_exchanges,
    get_all_p2p_binance_exchanges,
    get_binance_card_2_crypto_exchanges,
    get_binance_fiat_crypto_list,
    get_complex_binance_tinkoff_inter_exchanges_calculate,
    get_complex_binance_wise_inter_exchanges_calculate,
    get_simpl_binance_tinkoff_inter_exchanges_calculate,
    get_simpl_binance_wise_inter_exchanges_calculate)
from crypto_exchanges.filters import ExchangesFilter
from crypto_exchanges.models import (CryptoExchanges, InterExchanges,
                                     IntraCryptoExchanges,
                                     P2PCryptoExchangesRates)
from crypto_exchanges.serializers import InterExchangesSerializer


class CryptoExchangesRatesList(ListView):
    def get_queryset(self):
        return self.model.objects.filter(price__isnull=False)

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(CryptoExchangesRatesList,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class CryptoExchangeRatesList(ListView):
    def get_crypto_exchange_name(self):
        return self.kwargs.get('crypto_exchange_name').capitalize()

    def get_bank_name(self):
        return self.kwargs.get('bank_name').capitalize()

    def get_queryset(self):
        if self.get_crypto_exchange_name() != 'Crypto_exchanges':
            crypto_exchange = CryptoExchanges.objects.get(
                name=self.get_crypto_exchange_name())
            if self.get_bank_name() != 'Banks':
                bank = Banks.objects.get(name=self.get_bank_name())
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange, bank=bank,
                    price__isnull=False
                )
            else:
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange, price__isnull=False
                )
        else:
            bank = Banks.objects.get(name=self.get_bank_name())
            return self.model.objects.filter(bank=bank, price__isnull=False)

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(CryptoExchangeRatesList,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['crypto_exchange_name'] = self.get_crypto_exchange_name()
        context['bank_name'] = self.get_bank_name()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class CryptoExchangesInternalExchanges(CryptoExchangesRatesList):
    model = IntraCryptoExchanges
    template_name = 'crypto_exchanges/internal_crypto_exchanges.html'


class CryptoExchangeInternalExchanges(CryptoExchangeRatesList):
    model = IntraCryptoExchanges
    template_name = 'crypto_exchanges/internal_crypto_exchanges.html'

    def get_queryset(self):
        crypto_exchange = CryptoExchanges.objects.get(
            name=self.get_crypto_exchange_name())
        return self.model.objects.filter(crypto_exchange=crypto_exchange)

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(CryptoExchangeRatesList,
                        self).get_context_data(**kwargs)
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['crypto_exchange_name'] = self.get_crypto_exchange_name()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class CryptoExchangesP2PExchanges(CryptoExchangesRatesList):
    model = P2PCryptoExchangesRates
    template_name = 'crypto_exchanges/p2p_crypto_exchanges.html'


class CryptoExchangeP2PExchanges(CryptoExchangeRatesList):
    model = P2PCryptoExchangesRates
    template_name = 'crypto_exchanges/p2p_crypto_exchanges.html'


def p2p_binance(request):
    return get_all_p2p_binance_exchanges()


def binance_crypto(request):
    return get_all_binance_crypto_exchanges()


def card_2_wallet_2_crypto(request):
    return get_all_card_2_wallet_2_crypto_exchanges()


def binance_fiat_crypto_list(request):
    return get_binance_fiat_crypto_list()


def binance_card_2_crypto_exchanges(request):
    return get_binance_card_2_crypto_exchanges()


def simpl_binance_tinkoff_inter_exchanges_calculate(request):
    return get_simpl_binance_tinkoff_inter_exchanges_calculate()


def simpl_binance_wise_inter_exchanges_calculate(request):
    return get_simpl_binance_wise_inter_exchanges_calculate()


def complex_binance_tinkoff_inter_exchanges_calculate(request):
    return get_complex_binance_tinkoff_inter_exchanges_calculate()


def complex_binance_wise_inter_exchanges_calculate(request):
    return get_complex_binance_wise_inter_exchanges_calculate()


def get_tinkoff_p2p_binance_exchanges(request):
    binance_parser = TinkoffBinanceP2PParser()
    binance_parser.main()


def get_wise_p2p_binance_exchanges(request):
    binance_parser = WiseBinanceP2PParser()
    binance_parser.main()


class InterExchangesList(FilterView):
    model = InterExchanges
    template_name = ('crypto_exchanges/inter_exchanges.html')
    filterset_class = ExchangesFilter

    def get_queryset(self):
        qs = self.model.objects.prefetch_related(
            'input_bank', 'output_bank', 'bank_exchange',
            'input_crypto_exchange', 'output_crypto_exchange',
            'interim_crypto_exchange', 'second_interim_crypto_exchange',
            'update'
        ).filter(marginality_percentage__gt=-1)
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(InterExchangesList,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['loop_rates'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest('update'
                                                            ).update.updated
        return context


class InterExchangesListNew(FilterView):
    model = InterExchanges
    template_name = 'crypto_exchanges/new.html'
    filterset_class = ExchangesFilter

    def get_queryset(self):
        pass

    def get_context_data(self, **kwargs):

        context = super(InterExchangesListNew,
                        self).get_context_data(**kwargs)
        context['start'] = InfoLoop.objects.latest('updated').value
        return context


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
                    datetime.now(timezone.utc) - timedelta(minutes=15)
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
