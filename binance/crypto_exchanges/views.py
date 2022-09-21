from crypto_exchanges.crypto_exchanges_registration.binance import (
    get_all, get_all_binance_crypto_exchanges,
    get_all_card_2_wallet_2_crypto_exchanges, get_all_p2p_binance_exchanges,
    get_best_card_2_card_crypto_exchanges, get_best_crypto_exchanges,
    get_binance_card_2_crypto_exchanges, get_binance_fiat_crypto_list,
    get_inter_exchanges_calculate)


def p2p_binance(request):
    return get_all_p2p_binance_exchanges()


def binance_crypto(request):
    return get_all_binance_crypto_exchanges()


def card_2_wallet_2_crypto(request):
    return get_all_card_2_wallet_2_crypto_exchanges()


def binance_fiat_crypto_list(request):
    return get_binance_fiat_crypto_list()


def binance_card_2_crypto_exchanges(request):
    return get_binance_card_2_crypto_exchanges()


def binance_best_crypto_exchanges(request):
    return get_best_crypto_exchanges()


def binance_best_card_2_card_crypto_exchanges(request):
    return get_best_card_2_card_crypto_exchanges()


def binance_inter_exchanges_calculate(request):
    return get_inter_exchanges_calculate()


def all(request):
    return get_all()
