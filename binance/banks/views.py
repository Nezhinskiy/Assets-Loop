from banks.tinkoff import get_all_tinkoff
from banks.wise import get_all_wise


def tinkoff(request):
    return get_all_tinkoff()


def wise(request):
    return get_all_wise()
