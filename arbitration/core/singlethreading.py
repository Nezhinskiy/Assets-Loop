from datetime import datetime

from banks.singlethreading import all_banks_exchanges
from core.models import InfoLoop
from crypto_exchanges.crypto_exchanges_registration.binance import \
    get_inter_exchanges_calculate
from crypto_exchanges.singlethreading import all_crypto_exchanges


def all_exchanges_singlethreading():
    first_loop = InfoLoop.objects.latest('value')
    value = first_loop.value
    count = 5
    while value:
        print('single')
        new_loop = InfoLoop.objects.create(value=True)
        start_time = datetime.now()
        all_banks_exchanges(new_loop)
        all_crypto_exchanges(new_loop)
        get_inter_exchanges_calculate()
        count -= 1
        if not count:
            InfoLoop.objects.create(value=False)
        value = InfoLoop.objects.last().value
        duration = datetime.now() - start_time
        new_loop.all_exchanges = duration
        new_loop.save()
    first_loop.delete()
