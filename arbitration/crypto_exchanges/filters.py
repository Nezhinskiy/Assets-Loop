import django_filters

from crypto_exchanges.models import InterExchanges
from banks.banks_config import BANKS_CONFIG

BANK_CHOICES = tuple((bank, bank) for bank in BANKS_CONFIG.keys())

class ExchangesFilter(django_filters.FilterSet):
    spred__gt = django_filters.NumberFilter(
        field_name='marginality_percentage', lookup_expr='gt'
    )
    spred__lt = django_filters.NumberFilter(
        field_name='marginality_percentage', lookup_expr='lt'
    )
    input_bank__name = django_filters.MultipleChoiceFilter(choices=BANK_CHOICES, field_name='input_bank__name')
    #
    # release_year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
    # release_year__gt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gt')
    # release_year__lt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lt')
    #
    # manufacturer__name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = InterExchanges
        fields = ['spred__gt', 'spred__lt', 'input_bank__name']