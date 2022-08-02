from banks.models import FIATS_WISE, WiseExchanges, WiseUpdates
from calculations.inside_banks import InsideBanks
from calculations.models import InsideWiseUpdates, InsideWiseExchanges


class Wise(InsideBanks):
    fiats = FIATS_WISE
    Exchanges = WiseExchanges
    InsideExchanges = InsideWiseExchanges
    Updates = InsideWiseUpdates


def get_all_wise():
    wise_parser = Wise()
    message = wise_parser.main()
    return message
