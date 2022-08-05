from p2p_exchanges.binance import get_all_p2p_binance_exchanges, get_all_binance_crypto_exchanges


def p2p_binance(request):
    return get_all_p2p_binance_exchanges()


def binance_crypto(request):
    return get_all_binance_crypto_exchanges()
