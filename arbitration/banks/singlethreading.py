from datetime import datetime

from banks.banks_registration.tinkoff import get_all_tinkoff_exchanges
from banks.banks_registration.wise import get_all_wise_exchanges
from banks.currency_markets_registration.tinkoff_invest import \
    get_tinkoff_invest_exchanges
from core.intra_exchanges import BestBankIntraExchanges


def all_banks_exchanges_rates():
    get_all_tinkoff_exchanges()
    get_all_wise_exchanges()


def all_banks_alternative_exchanges():
    get_tinkoff_invest_exchanges()


def best_bank_intra_exchanges():
    get_best_bank_intra_exchanges = BestBankIntraExchanges()
    get_best_bank_intra_exchanges.main()


def all_banks_exchanges(new_loop):
    start_time = datetime.now()
    all_banks_exchanges_rates()
    all_banks_alternative_exchanges()
    best_bank_intra_exchanges()
    duration = datetime.now() - start_time
    new_loop.all_banks_exchanges = duration
    new_loop.save()
