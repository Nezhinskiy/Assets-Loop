from parses_p2p.binance import get_all_p2p_binance


def index(request):
    return get_all_p2p_binance()
