from banks.tinkoff import get_all_tinkoff_exchanges
from banks.wise import get_all_wise_exchanges


def tinkoff(request):
    return get_all_tinkoff_exchanges()


def wise(request):
    return get_all_wise_exchanges()
