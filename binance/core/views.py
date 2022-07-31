from parses_p2p.parse import get_all_p2p_binance
from banks.tinkoff import get_all_tinkoff


def index(request):
    get_all_p2p_binance()
    get_all_tinkoff()
    return 'успех'
