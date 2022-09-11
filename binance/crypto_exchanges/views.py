from crypto_exchanges.crypto_exchanges_registration.binance import (
    get_all_binance_crypto_exchanges, get_all_p2p_binance_exchanges,
    get_all_card_2_fiat_2_crypto_exchanges)


def p2p_binance(request):
    return get_all_p2p_binance_exchanges()


def binance_crypto(request):
    return get_all_binance_crypto_exchanges()


def card_2_fiat_2_crypto(request):
    return get_all_card_2_fiat_2_crypto_exchanges()
