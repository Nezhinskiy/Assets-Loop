from banks.banks_registration.tinkoff import (
    TINKOFF_CURRENCIES, TINKOFF_CURRENCIES_WITH_REQUISITES, TinkoffParser)
from banks.banks_registration.wise import WISE_CURRENCIES, WiseParser
from crypto_exchanges.models import P2PCryptoExchangesRates

BANKS_CONFIG = {
    'Tinkoff': {
        'bank_parser': TinkoffParser,
        'currencies': TINKOFF_CURRENCIES,
        'currencies_with_requisites': TINKOFF_CURRENCIES_WITH_REQUISITES,
        'crypto_exchanges': ('Binance',),
        'payment_channels': (
            P2PCryptoExchangesRates,
        ),
        'transaction_methods': (),
        'bank_invest_exchanges': ['Tinkoff invest']
    },
    'Wise': {
        'bank_parser': WiseParser,
        'currencies': WISE_CURRENCIES,
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
