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


class ExchangesFilter(django_filters.FilterSet):
    spred__gte = django_filters.NumberFilter(
        field_name='marginality_percentage', lookup_expr='gte',
        label='от', help_text='От'
    )
    spred__lte = django_filters.NumberFilter(
        field_name='marginality_percentage', lookup_expr='lte',
        label='до', help_text='До'
    )
    crypto_exchange__name = django_filters.MultipleChoiceFilter(
        choices=CRYPTO_EXCHANGE_CHOICES, field_name='crypto_exchange__name',
        widget=Select2MultipleWidget, label='Крипто биржи'
    )
    crypto_exchange__asset = django_filters.MultipleChoiceFilter(
        choices=CRYPTO_EXCHANGE_ASSET_CHOICES,
        method='asset_filter',
        widget=Select2MultipleWidget, label='Криптовалюты'
    )
    input_bank__name = django_filters.MultipleChoiceFilter(
        choices=BANK_CHOICES, field_name='input_bank__name',
        widget=Select2MultipleWidget, label='Банки на входе'
    )
    output_bank__name = django_filters.MultipleChoiceFilter(
        choices=BANK_CHOICES, field_name='output_bank__name',
        widget=Select2MultipleWidget, label='Банки на выходе',
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

    class Meta:
        model = InterExchanges
        fields = [
            'spred__gte', 'spred__lte',
            'input_bank__name', 'output_bank__name', 'crypto_exchange__name',
            'crypto_exchange__asset',
        ]
