from banks.tinkoff import get_all_tinkoff
from banks.wise import get_all_wise
from p2p_exchanges.binance import get_all_p2p_binance


def index(request):
    get_all_p2p_binance()
    get_all_tinkoff()
    get_all_wise()
    return 'успех'
