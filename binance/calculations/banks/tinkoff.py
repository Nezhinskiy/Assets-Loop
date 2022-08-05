from bank_rates.models import TinkoffExchanges, FIATS_TINKOFF
from calculations.inside_banks import InsideBanks
from calculations.models import InsideTinkoffUpdates, InsideTinkoffExchanges
from bank_rates.banks.tinkoff import get_all_tinkoff_exchanges, TINKOFF_CURRENCIES_WITH_REQUISITES


class Tinkoff(InsideBanks):
    fiats = FIATS_TINKOFF
    Exchanges = TinkoffExchanges
    InsideExchanges = InsideTinkoffExchanges
    Updates = InsideTinkoffUpdates
    currencies_with_requisites = TINKOFF_CURRENCIES_WITH_REQUISITES


def get_all_tinkoff():
    get_all_tinkoff_exchanges()
    tinkoff_insider = Tinkoff()
    message = tinkoff_insider.main()
    return message
