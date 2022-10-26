from datetime import datetime
from arbitration.celery import app
from dateutil import parser
from core.models import InfoLoop
from crypto_exchanges.crypto_exchanges_registration.binance import BinanceInterExchangesCalculate

from crypto_exchanges.crypto_exchanges_registration.binance import \
    ComplexBinanceWiseInterExchangesCalculate, \
    ComplexBinanceTinkoffInterExchangesCalculate, \
    SimplBinanceWiseInterExchangesCalculate, \
    SimplBinanceTinkoffInterExchangesCalculate


@app.task
def all_start_time():
    return datetime.now()


@app.task
def get_simpl_binance_tinkoff_inter_exchanges_calculate(_):
    simpl_binance_tinkoff_inter_exchanges_calculate = (
        SimplBinanceTinkoffInterExchangesCalculate()
    )
    simpl_binance_tinkoff_inter_exchanges_calculate.main()


@app.task
def get_simpl_binance_wise_inter_exchanges_calculate(_):
    simpl_binance_wise_inter_exchanges_calculate = (
        SimplBinanceWiseInterExchangesCalculate()
    )
    simpl_binance_wise_inter_exchanges_calculate.main()


@app.task
def get_complex_binance_tinkoff_inter_exchanges_calculate(_):
    complex_binance_tinkoff_inter_exchanges_calculate = (
        ComplexBinanceTinkoffInterExchangesCalculate()
    )
    complex_binance_tinkoff_inter_exchanges_calculate.main()


@app.task
def get_complex_binance_wise_inter_exchanges_calculate(_):
    complex_binance_wise_inter_exchanges_calculate = (
        ComplexBinanceWiseInterExchangesCalculate()
    )
    complex_binance_wise_inter_exchanges_calculate.main()


# Best crypto exchanges
@app.task
def all_end(_):
    print('all end')


@app.task
def best_get_inter_exchanges_calculate(str_start_time):
    start_time = parser.parse(str_start_time[0])
    print('crypto_exchanges_end')
    duration = datetime.now() - start_time
    new_loop = InfoLoop.objects.filter(value=True).last()
    new_loop.all_exchanges = duration
    new_loop.save()
