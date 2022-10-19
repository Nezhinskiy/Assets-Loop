from datetime import datetime

from crypto_exchanges.crypto_exchanges_registration.binance import (
    get_all_binance_crypto_exchanges, get_all_card_2_wallet_2_crypto_exchanges,
    get_all_p2p_binance_exchanges, get_best_card_2_card_crypto_exchanges,
    get_best_crypto_exchanges, get_binance_card_2_crypto_exchanges,
    get_binance_fiat_crypto_list)


def first_crypto_exchanges_rates():
    get_all_p2p_binance_exchanges()
    get_all_binance_crypto_exchanges()
    get_binance_fiat_crypto_list()


def second_crypto_exchanges_rates():
    get_binance_card_2_crypto_exchanges()
    get_all_card_2_wallet_2_crypto_exchanges()


def all_crypto_exchanges(new_loop):
    start_time = datetime.now()
    first_crypto_exchanges_rates()
    second_crypto_exchanges_rates()
    get_best_crypto_exchanges()
    get_best_card_2_card_crypto_exchanges()
    duration = datetime.now() - start_time
    new_loop.all_crypto_exchanges = duration
    new_loop.save()
