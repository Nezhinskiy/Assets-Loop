from threading import Thread
from datetime import datetime

from crypto_exchanges.crypto_exchanges_registration.binance import (
    get_all_binance_crypto_exchanges,
    get_all_card_2_wallet_2_crypto_exchanges, get_all_p2p_binance_exchanges,
    get_best_card_2_card_crypto_exchanges, get_best_crypto_exchanges,
    get_binance_card_2_crypto_exchanges, get_binance_fiat_crypto_list)


def first_crypto_exchanges_rates():
    all_p2p_binance_exchanges = Thread(target=get_all_p2p_binance_exchanges)
    all_binance_crypto_exchanges = Thread(
        target=get_all_binance_crypto_exchanges)
    binance_fiat_crypto_list = Thread(target=get_binance_fiat_crypto_list)
    all_p2p_binance_exchanges.start()
    all_binance_crypto_exchanges.start()
    binance_fiat_crypto_list.start()
    all_p2p_binance_exchanges.join()
    all_binance_crypto_exchanges.join()
    binance_fiat_crypto_list.join()


def second_crypto_exchanges_rates():
    binance_card_2_crypto_exchanges = Thread(
        target=get_binance_card_2_crypto_exchanges)
    all_card_2_wallet_2_crypto_exchanges = Thread(
        target=get_all_card_2_wallet_2_crypto_exchanges)
    binance_card_2_crypto_exchanges.start()
    all_card_2_wallet_2_crypto_exchanges.start()
    binance_card_2_crypto_exchanges.join()
    all_card_2_wallet_2_crypto_exchanges.join()


def all_crypto_exchanges():
    start_time = datetime.now()
    first_crypto_exchanges_rates()
    second_crypto_exchanges_rates()
    get_best_crypto_exchanges()
    get_best_card_2_card_crypto_exchanges()
    duration = datetime.now() - start_time
    print('all_crypto_exchanges', duration)
