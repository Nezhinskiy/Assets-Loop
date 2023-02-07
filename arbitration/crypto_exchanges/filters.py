import time

import django_filters
from django import forms
from django.db.models import Q
from django_select2.forms import Select2MultipleWidget

from banks.banks_config import BANKS_CONFIG
from core.parsers import check_work_time
from crypto_exchanges.crypto_exchanges_config import CRYPTO_EXCHANGES_CONFIG
from crypto_exchanges.models import InterExchanges

BANK_CHOICES = tuple((bank, bank) for bank in BANKS_CONFIG.keys())
CRYPTO_EXCHANGE_CHOICES = tuple(
    (crypto_exchange, crypto_exchange)
    for crypto_exchange in list(CRYPTO_EXCHANGES_CONFIG.keys())[1:]
)
CRYPTO_EXCHANGE_ASSET_CHOICES = tuple(
    (asset, asset)
    for asset in ('USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'SHIB', 'RUB', 'ADA')
)
PAYMENT_CHANNEL_CHOICES = (
    ('P2P', 'P2P'),
    ('Card2CryptoExchange', 'Card2CryptoExchange'),
    ('Card2Wallet2CryptoExchange', 'Card2Wallet2CryptoExchange')
)
ALL_FIAT_CHOICES = tuple(
    (fiat, fiat) for fiat in CRYPTO_EXCHANGES_CONFIG['all_fiats']
)
BANK_EXCHANGE_CHOICES = (
    (0, 'Да'),
    (1, 'Нет'),
    ('banks', 'Только внутри банков'),
    ('Tinkoff invest', 'Только через валютные биржи')
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
    payment_channel = django_filters.MultipleChoiceFilter(
        choices=PAYMENT_CHANNEL_CHOICES,
        method='payment_channel_filter',
        widget=Select2MultipleWidget, label='Платёжные методы',
        help_text=(
            '•P2P (peer-to-peer) — прямая торговля пользователей '
            'друг с другом на бирже. Комиссия не взымается. '
            '•Card2CryptoExchange — ввод / вывод криптоактивов '
            'напрямую через биржу. Предусмотрена комиссия. '
            '•Card2Wallet2CryptoExchange — ввод на биржу сначала '
            'фиатных денег, с последующим обменом на СПОТовой бирже '
            'в криптоактивы или наоборот вывод с предворительным '
            'обменом криптоактивов в фиатные деньги. '
            'Предусмотрена комиссия.'
        )
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
        choices=ALL_FIAT_CHOICES,
        method='fiat_filter',
        widget=Select2MultipleWidget, label='Валюты'
    )
    bank_exchange = django_filters.ChoiceFilter(
        choices=BANK_EXCHANGE_CHOICES, method='bank_exchange_filter',
        label='Внутрибанковская конвертация', empty_label='', help_text=(
            '•Да - только связки с внутрибанковской конвертацией. '
            '•Нет - только связки без внутрибанковской конвертации. '
            '*Через валютные биржи можно обменивать только по рабочим дням '
            'с 7:00 до 19:00 по Мск, в остальное время этот фильтр недоступен'
        )
    )

    def asset_filter(self, queryset, _, values):
        return queryset.filter(
            input_crypto_exchange__asset__in=values,
            output_crypto_exchange__asset__in=values
        )

    def payment_channel_filter(self, queryset, _, values):
        return queryset.filter(
            input_crypto_exchange__payment_channel__in=values,
            output_crypto_exchange__payment_channel__in=values
        )

    def fiat_filter(self, queryset, _, values):
        return queryset.filter(
            input_crypto_exchange__fiat__in=values,
            output_crypto_exchange__fiat__in=values
        )

    def bank_exchange_filter(self, queryset, _, values):
        if values in ('1', '0'):
            qs = queryset.filter(
                bank_exchange__isnull=bool(int(values))
            )
        elif values == 'banks':
            qs = queryset.filter(
                bank_exchange__isnull=False,
                bank_exchange__currency_market__isnull=True
            )
        else:
            qs = queryset.filter(
                bank_exchange__isnull=False,
                bank_exchange__currency_market__isnull=False
            )
        return qs

    class Meta:
        model = InterExchanges
        fields = [
            'gte', 'lte', 'input_bank', 'output_bank', 'fiats',
            'bank_exchange', 'crypto_exchange', 'assets', 'payment_channel'
        ]
