from datetime import datetime, timezone
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
def start_crypto_exchanges():
    info = InfoLoop.objects.last()
    info.start_crypto_exchanges = datetime.now(timezone.utc)
    info.save()
    print('start_crypto_exchanges')


@app.task
def start_bank_exchanges():
    info = InfoLoop.objects.last()
    info.start_banks_exchanges = datetime.now(timezone.utc)
    info.save()
    print('start_banks_exchanges')


@app.task
def end_all_exchanges(_):
    info = InfoLoop.objects.filter(value=True).last()
    duration = datetime.now(timezone.utc) - info.updated
    info.all_exchanges = duration
    info.save()
    print('end_all_exchanges')


@app.task
def end_crypto_exchanges(_):
    info = InfoLoop.objects.filter(value=True).last()
    duration = datetime.now(timezone.utc) - info.updated
    info.all_crypto_exchanges = duration
    info.save()
    print('end_crypto_exchanges')


@app.task
def end_banks_exchanges(_):
    info = InfoLoop.objects.filter(value=True).last()
    duration = datetime.now(timezone.utc) - info.updated
    info.all_banks_exchanges = duration
    info.save()
    print('end_banks_exchanges')


@app.task
def get_simpl_binance_tinkoff_inter_exchanges_calculate(_):
    simpl_binance_tinkoff_inter_exchanges_calculate = (
        SimplBinanceTinkoffInterExchangesCalculate()
    )
    simpl_binance_tinkoff_inter_exchanges_calculate.main()
    print('simpl_binance_tinkoff')


@app.task
def get_simpl_binance_wise_inter_exchanges_calculate(_):
    simpl_binance_wise_inter_exchanges_calculate = (
        SimplBinanceWiseInterExchangesCalculate()
    )
    simpl_binance_wise_inter_exchanges_calculate.main()
    print('simpl_binance_wise')


@app.task
def get_complex_binance_tinkoff_inter_exchanges_calculate(_):
    complex_binance_tinkoff_inter_exchanges_calculate = (
        ComplexBinanceTinkoffInterExchangesCalculate()
    )
    complex_binance_tinkoff_inter_exchanges_calculate.main()
    print('complex_binance_tinkoff')


@app.task
def get_complex_binance_wise_inter_exchanges_calculate(_):
    complex_binance_wise_inter_exchanges_calculate = (
        ComplexBinanceWiseInterExchangesCalculate()
    )
    complex_binance_wise_inter_exchanges_calculate.main()
    print('complex_binance_wise')
