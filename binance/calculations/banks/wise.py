from bank_rates.models import FIATS_WISE, WiseExchanges, WiseUpdates
from calculations.inside_banks import InsideBanks
from calculations.models import InsideWiseUpdates, InsideWiseExchanges
from bank_rates.banks.wise import get_all_wise_exchanges


class Wise(InsideBanks):
    fiats = FIATS_WISE
    Exchanges = WiseExchanges
    InsideExchanges = InsideWiseExchanges
    Updates = InsideWiseUpdates


def get_all_wise():
    get_all_wise_exchanges()
    wise_insider = Wise()
    message = wise_insider.main()
    return message
