from banks.models import TinkoffExchanges, FIATS_TINKOFF
from calculations.inside_banks import InsideBanks
from calculations.models import InsideTinkoffUpdates, InsideTinkoffExchanges
from banks.tinkoff import get_all_tinkoff_exchanges


class Tinkoff(InsideBanks):
    fiats = FIATS_TINKOFF
    Exchanges = TinkoffExchanges
    InsideExchanges = InsideTinkoffExchanges
    Updates = InsideTinkoffUpdates


def get_all_tinkoff():
    get_all_tinkoff_exchanges()
    tinkoff_insider = Tinkoff()
    message = tinkoff_insider.main()
    return message
