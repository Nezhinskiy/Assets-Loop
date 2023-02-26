from banks.banks_registration.tinkoff import (
    TINKOFF_CURRENCIES, TinkoffParser)
from banks.banks_registration.wise import WISE_CURRENCIES, WiseParser
from crypto_exchanges.models import P2PCryptoExchangesRates
from banks.banks_registration.sberbank import SBERBANK_CURRENCIES

BANKS_CONFIG = {
    'Tinkoff': {
        'bank_parser': TinkoffParser,
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
        'bank_parser': None,
        'currencies': SBERBANK_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'RosBankNew',
        'payment_channels': (
            P2PCryptoExchangesRates,
        ),
        'transaction_methods': (),
        'bank_invest_exchanges': []
    },
    'Wise': {
        'bank_parser': WiseParser,
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
