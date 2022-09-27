from threading import Thread
from datetime import datetime

from banks.banks_registration.tinkoff import (get_all_tinkoff_exchanges,
                                              get_tinkoff_not_looped,
                                              get_tinkoff_invest_exchanges)
from banks.banks_registration.wise import get_all_wise_exchanges, get_wise_not_looped
from core.intra_exchanges import BestBankIntraExchanges


def all_banks_exchanges_rates():
    all_tinkoff_exchanges = Thread(target=get_all_tinkoff_exchanges)
    all_wise_exchanges = Thread(target=get_all_wise_exchanges)
    all_tinkoff_exchanges.start()
    all_wise_exchanges.start()
    all_tinkoff_exchanges.join()
    all_wise_exchanges.join()


def all_banks_alternative_exchanges():
    tinkoff_not_looped = Thread(target=get_tinkoff_not_looped)
    tinkoff_invest_exchanges = Thread(target=get_tinkoff_invest_exchanges)
    wise_not_looped = Thread(target=get_wise_not_looped)
    tinkoff_not_looped.start()
    tinkoff_invest_exchanges.start()
    wise_not_looped.start()
    tinkoff_not_looped.join()
    tinkoff_invest_exchanges.join()
    wise_not_looped.join()


def best_bank_intra_exchanges():
    get_best_bank_intra_exchanges = BestBankIntraExchanges()
    get_best_bank_intra_exchanges.main()


def all_banks_exchanges():
    start_time = datetime.now()
    all_banks_exchanges_rates()
    all_banks_alternative_exchanges()
    best_bank_intra_exchanges()
    duration = datetime.now() - start_time
    print('all_banks_exchanges', duration)
