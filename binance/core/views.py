from banks.tinkoff import get_all_tinkoff_exchanges
from banks.wise import get_all_wise_exchanges
from p2p_exchanges.binance import get_all_p2p_binance_exchanges


def index(request):
    get_all_p2p_binance()
    get_all_tinkoff()
    get_all_wise()
    return 'успех'
