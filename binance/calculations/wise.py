from banks.models import FIATS_WISE, WiseExchanges, WiseUpdates
from calculations.inside_banks import InsideBanks


class Wise(InsideBanks):
    fiats = FIATS_WISE
    Exchanges = WiseExchanges
    Updates = WiseUpdates


def get_all_wise():
    wise_parser = Wise()
    message = wise_parser.main_loop()
    return message
