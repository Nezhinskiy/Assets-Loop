from banks.tinkoff import get_all_tinkoff
from parses_p2p.parse import get_all_p2p_binance


def index(request):
    get_all_p2p_binance()
    get_all_tinkoff()
    return 'успех'
