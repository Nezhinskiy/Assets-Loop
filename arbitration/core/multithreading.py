from datetime import datetime
from threading import Thread

from banks.multithreading import all_banks_exchanges
from core.models import InfoLoop
from crypto_exchanges.multithreading import all_crypto_exchanges


def all_exchanges():
    first_loop = InfoLoop.objects.latest('value')
    value = first_loop.value
    count = 5
    while value:
        new_loop = InfoLoop.objects.create(value=True)
        start_time = datetime.now()
        banks_exchanges = Thread(
            target=all_banks_exchanges, args=(new_loop,))
        crypto_exchanges = Thread(
            target=all_crypto_exchanges, args=(new_loop,))
        banks_exchanges.start()
        crypto_exchanges.start()
        banks_exchanges.join()
        crypto_exchanges.join()
        count -= 1
        if not count:
            InfoLoop.objects.create(value=False)
        value = InfoLoop.objects.last().value
        duration = datetime.now() - start_time
        new_loop.all_exchanges = duration
        new_loop.save()
    first_loop.delete()
