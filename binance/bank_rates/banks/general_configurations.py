from bank_rates.banks.tinkoff import TINKOFF_CURRENCIES_WITH_REQUISITES
from bank_rates.models import FIATS_TINKOFF, TinkoffExchanges, TinkoffUpdates
from calculations.models import InsideTinkoffExchanges, InsideTinkoffUpdates

BANKING_CONFIG = {
    'Tinkoff': {
        'BANK_CURRENCIES': FIATS_TINKOFF,
        'BANK_CURRENCIES_WITH_REQUISITES': TINKOFF_CURRENCIES_WITH_REQUISITES,
        'bank_exchange_rates': TinkoffExchanges,
        'bank_rates_updates': TinkoffUpdates,
        'inside_bank_exchanges': InsideTinkoffExchanges,
        'internal_bank_exchanges': InsideTinkoffExchanges,
        'internal_bank_updates': InsideTinkoffUpdates
    },
}
