from banks.banks_registration.tinkoff import (
    TINKOFF_CURRENCIES)
from banks.banks_registration.wise import WISE_CURRENCIES
from crypto_exchanges.models import P2PCryptoExchangesRates
from banks.banks_registration.sberbank import SBERBANK_CURRENCIES

from banks.banks_registration.raiffeisen import \
    RAIFFEISEN_CURRENCIES

from banks.banks_registration.qiwi import QIWI_CURRENCIES

from banks.banks_registration.yoomoney import YOOMONEY_CURRENCIES

BANKS_CONFIG = {
    'Tinkoff': {
        'bank_parser': True,
        'currencies': TINKOFF_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'TinkoffNew',
        'payment_channels': (
            P2PCryptoExchangesRates,
        ),
        'transaction_methods': (),
        'bank_invest_exchanges': ['Tinkoff invest']
    },
    'Sberbank': {
        'bank_parser': False,
        'currencies': SBERBANK_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'RosBankNew',
        'payment_channels': (
            P2PCryptoExchangesRates,
        ),
        'transaction_methods': (),
        'bank_invest_exchanges': []
    },
    'Raiffeisen': {
        'bank_parser': True,
        'currencies': RAIFFEISEN_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'RaiffeisenBank',
        'payment_channels': (
            P2PCryptoExchangesRates,
        ),
        'transaction_methods': (),
        'bank_invest_exchanges': []
    },
    'QIWI': {
        'bank_parser': False,
        'currencies': QIWI_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'QIWI',
        'payment_channels': (
            P2PCryptoExchangesRates,
        ),
        'transaction_methods': (),
        'bank_invest_exchanges': []
    },
    'Yoomoney': {
        'bank_parser': False,
        'currencies': YOOMONEY_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'YandexMoneyNew',
        'payment_channels': (
            P2PCryptoExchangesRates,
        ),
        'transaction_methods': (),
        'bank_invest_exchanges': []
    },
    'Wise': {
        'bank_parser': True,
        'currencies': WISE_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'Wise',
        'payment_channels': (
            'Card2CryptoExchange', 'Card2Wallet2CryptoExchange',
            P2PCryptoExchangesRates
        ),
        'transaction_methods': (
            'SettlePay (Visa/MC)', 'Bank Card (Visa/MC)', 'Bank Card (Visa)'
        ),
        'bank_invest_exchanges': []
    }
}

INTERNATIONAL_BANKS = ('Wise',)
