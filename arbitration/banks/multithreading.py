from datetime import datetime
from threading import Thread

from banks.banks_registration.tinkoff import get_all_tinkoff_exchanges
from banks.banks_registration.wise import get_all_wise_exchanges
from banks.currency_markets_registration.tinkoff_invest import \
    get_tinkoff_invest_exchanges
from core.intra_exchanges import BestBankIntraExchanges


def all_banks_exchanges_rates():
    all_tinkoff_exchanges = Thread(target=get_all_tinkoff_exchanges)
    all_wise_exchanges = Thread(target=get_all_wise_exchanges)
    all_tinkoff_exchanges.start()
    all_wise_exchanges.start()
    all_tinkoff_exchanges.join()
    all_wise_exchanges.join()


def all_banks_alternative_exchanges():
    tinkoff_invest_exchanges = Thread(target=get_tinkoff_invest_exchanges)
    tinkoff_invest_exchanges.start()
    tinkoff_invest_exchanges.join()


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
