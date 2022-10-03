from datetime import datetime
from threading import Thread

from banks.multithreading import all_banks_exchanges
from crypto_exchanges.crypto_exchanges_registration.binance import \
    get_inter_exchanges_calculate
from crypto_exchanges.multithreading import all_crypto_exchanges


def all_exchanges():
    start_time = datetime.now()
    crypto_exchanges = Thread(target=all_crypto_exchanges)
    banks_exchanges = Thread(target=all_banks_exchanges)
    crypto_exchanges.start()
    banks_exchanges.start()
    crypto_exchanges.join()
    banks_exchanges.join()
    get_inter_exchanges_calculate()
    duration = datetime.now() - start_time
    print('all_exchanges', duration)