from banks.banks_registration.bank_of_georgia import BOG_CURRENCIES
from banks.banks_registration.credo import CREDO_CURRENCIES
from banks.banks_registration.qiwi import QIWI_CURRENCIES
from banks.banks_registration.raiffeisen import RAIFFEISEN_CURRENCIES
from banks.banks_registration.sberbank import SBERBANK_CURRENCIES
from banks.banks_registration.tbc import TBC_CURRENCIES
from banks.banks_registration.tinkoff import TINKOFF_CURRENCIES
from banks.banks_registration.wise import WISE_CURRENCIES
from banks.banks_registration.yoomoney import YOOMONEY_CURRENCIES

INTERNATIONAL_BANKS = ('Wise', 'Bank of Georgia', 'TBC', 'Credo')
RUS_BANKS = ('Tinkoff', 'Sberbank', 'Raiffeisen', 'QIWI', 'Yoomoney')

BANKS_CONFIG = {
    'Tinkoff': {
        'bank_parser': True,
        'currencies': TINKOFF_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'TinkoffNew',
        'bybit_name': '75',
        'payment_channels': ('P2P',),
        'transaction_methods': (),
        'bank_invest_exchanges': ['Tinkoff invest']
    },
    'Sberbank': {
        'bank_parser': False,
        'currencies': SBERBANK_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'RosBankNew',
        'bybit_name': '185',
        'payment_channels': ('P2P',),
        'transaction_methods': (),
        'bank_invest_exchanges': []
    },
    'Raiffeisen': {
        'bank_parser': True,
        'currencies': RAIFFEISEN_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'RaiffeisenBank',
        'bybit_name': '64',
        'payment_channels': ('P2P',),
        'transaction_methods': (),
        'bank_invest_exchanges': ()
    },
    'QIWI': {
        'bank_parser': False,
        'currencies': QIWI_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'QIWI',
        'bybit_name': '62',
        'payment_channels': ('P2P',),
        'transaction_methods': (),
        'bank_invest_exchanges': ()
    },
    'Yoomoney': {
        'bank_parser': False,
        'currencies': YOOMONEY_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'YandexMoneyNew',
        'bybit_name': '274',
        'payment_channels': ('P2P',),
        'transaction_methods': (),
        'bank_invest_exchanges': ()
    },
    'Bank of Georgia': {
        'bank_parser': False,
        'currencies': BOG_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'BankofGeorgia',
        'bybit_name': '11',
        'payment_channels': (
            'Card2CryptoExchange', 'P2P'
        ),
        'transaction_methods': (
            'Bank Card (Visa/MC)', 'Bank Card (Visa)'
        ),
        'bank_invest_exchanges': ()
    },
    'TBC': {
        'bank_parser': False,
        'currencies': TBC_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'TBCbank',
        'bybit_name': '165',
        'payment_channels': (
            'Card2CryptoExchange', 'P2P'
        ),
        'transaction_methods': (
            'Bank Card (Visa/MC)', 'Bank Card (Visa)'
        ),
        'bank_invest_exchanges': ()
    },
    'Credo': {
        'bank_parser': False,
        'currencies': CREDO_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'CREDOBANK',
        'bybit_name': '359',
        'payment_channels': (
            'Card2CryptoExchange', 'P2P'
        ),
        'transaction_methods': (
            'Bank Card (Visa/MC)', 'Bank Card (Visa)'
        ),
        'bank_invest_exchanges': ()
    },
    'Wise': {
        'bank_parser': True,
        'currencies': WISE_CURRENCIES,
        'crypto_exchanges': ('Binance',),
        'binance_name': 'Wise',
        'bybit_name': '78',
        'payment_channels': (
            'Card2CryptoExchange', 'Card2Wallet2CryptoExchange', 'P2P'
        ),
        'transaction_methods': (
            'Bank Card (Visa/MC)', 'Bank Card (Visa)'
        ),
        'bank_invest_exchanges': ()
    }
}
