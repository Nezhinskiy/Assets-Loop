from datetime import datetime
from arbitration.celery import app
from dateutil import parser
from core.models import InfoLoop
from crypto_exchanges.crypto_exchanges_registration.binance import BinanceInterExchangesCalculate


@app.task
def all_start_time():
    return datetime.now()


# Best crypto exchanges
@app.task
def best_get_inter_exchanges_calculate(str_start_time):
    start_time = parser.parse(str_start_time[0])
    inter_exchanges_calculate = BinanceInterExchangesCalculate()
    inter_exchanges_calculate.main()
    print('crypto_exchanges_end')
    duration = datetime.now() - start_time
    new_loop = InfoLoop.objects.filter(value=True).last()
    new_loop.all_exchanges = duration
    new_loop.save()
