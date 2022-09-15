from banks.banks_registration.tinkoff import (
    TINKOFF_CURRENCIES, TINKOFF_CURRENCIES_WITH_REQUISITES, IntraTinkoff,
    TinkoffParser)
from banks.banks_registration.wise import IntraWise, WiseParser

BANKS_CONFIG = {
    'Tinkoff': {
        'bank_parser': TinkoffParser,
        'intra_exchange': IntraTinkoff,
        'currencies': TINKOFF_CURRENCIES,
        'currencies_with_requisites': TINKOFF_CURRENCIES_WITH_REQUISITES,
        'crypto_exchanges': ('Binance',)
    },
    'Wise': {
        'bank_parser': WiseParser,
        'intra_exchange': IntraWise,
        'currencies': TINKOFF_CURRENCIES,
    }
}
