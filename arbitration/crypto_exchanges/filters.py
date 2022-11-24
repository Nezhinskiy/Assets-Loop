import time

import django_filters
from django.db.models import Q

from crypto_exchanges.models import InterExchanges
from banks.banks_config import BANKS_CONFIG
from crypto_exchanges.crypto_exchanges_config import CRYPTO_EXCHANGES_CONFIG
from django_select2.forms import Select2MultipleWidget


BANK_CHOICES = tuple((bank, bank) for bank in BANKS_CONFIG.keys())
CRYPTO_EXCHANGE_CHOICES = tuple(
    (crypto_exchange, crypto_exchange)
    for crypto_exchange in list(CRYPTO_EXCHANGES_CONFIG.keys())[1:]
)
CRYPTO_EXCHANGE_ASSET_CHOICES = tuple(
    (asset, asset)
    for asset in ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'SHIB', 'RUB', 'ADA')
)
ALL_FIATS = tuple(
    (fiat, fiat) for fiat in CRYPTO_EXCHANGES_CONFIG['all_fiats']
)


class ExchangesFilter(django_filters.FilterSet):
    gte = django_filters.NumberFilter(
        field_name='marginality_percentage', lookup_expr='gte',
        label='от', help_text='От'
    )
    lte = django_filters.NumberFilter(
        field_name='marginality_percentage', lookup_expr='lte',
        label='до', help_text='До'
    )
    crypto_exchange = django_filters.MultipleChoiceFilter(
        choices=CRYPTO_EXCHANGE_CHOICES, field_name='crypto_exchange__name',
        widget=Select2MultipleWidget, label='Крипто биржи'
    )
    assets = django_filters.MultipleChoiceFilter(
        choices=CRYPTO_EXCHANGE_ASSET_CHOICES,
        method='asset_filter',
        widget=Select2MultipleWidget, label='Криптоактивы'
    )
    input_bank = django_filters.MultipleChoiceFilter(
        choices=BANK_CHOICES, field_name='input_bank__name',
        widget=Select2MultipleWidget, label='Банки в начале'
    )
    output_bank = django_filters.MultipleChoiceFilter(
        choices=BANK_CHOICES, field_name='output_bank__name',
        widget=Select2MultipleWidget, label='Банки в конце',
    )
    fiats = django_filters.MultipleChoiceFilter(
        choices=ALL_FIATS,
        method='fiat_filter',
        widget=Select2MultipleWidget, label='Валюты'
    )
    #
    # release_year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
    # release_year__gt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gt')
    # release_year__lt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lt')
    #
    # manufacturer__name = django_filters.CharFilter(lookup_expr='icontains')

    def asset_filter(self, queryset, _, values):
        return queryset.filter(
            input_crypto_exchange__asset__in=values,
            output_crypto_exchange__asset__in=values
        )

    def fiat_filter(self, queryset, _, values):
        return queryset.filter(
            bank_exchange__from_fit__in=values,
            bank_exchange__to_fit__in=values
        )

    class Meta:
        model = InterExchanges
        fields = [
            'gte', 'lte', 'input_bank', 'output_bank', 'fiats',
            'crypto_exchange', 'assets'
        ]
