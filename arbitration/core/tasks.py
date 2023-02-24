import logging
import random
import re
import subprocess
from abc import ABC
from datetime import datetime, timezone, timedelta
from time import sleep

from celery import chord, group, shared_task
from arbitration.celery import app
from banks.tasks import (best_bank_intra_exchanges,
                         parse_currency_market_tinkoff_rates,
                         parse_internal_tinkoff_rates,
                         parse_internal_wise_rates)
from core.models import InfoLoop
from core.registration import all_registration
from crypto_exchanges.crypto_exchanges_registration.binance import (
    ComplexBinanceTinkoffInterExchangesCalculate,
    ComplexBinanceWiseInterExchangesCalculate,
    SimplBinanceTinkoffInterExchangesCalculate,
    SimplBinanceWiseInterExchangesCalculate)
from crypto_exchanges.tasks import (
                                    crypto_exchanges_start_time,
                                    get_all_binance_crypto_exchanges,
                                    get_all_card_2_wallet_2_crypto_exchanges_buy,
                                    get_all_card_2_wallet_2_crypto_exchanges_sell,
                                    get_binance_card_2_crypto_exchanges_buy,
                                    get_binance_card_2_crypto_exchanges_sell,
                                    get_tinkoff_p2p_binance_exchanges,
                                    get_wise_p2p_binance_exchanges
                                    )

from fake_useragent import UserAgent
from stem.control import Controller
from stem import Signal
import requests

from crypto_exchanges.models import InterExchanges

from crypto_exchanges.crypto_exchanges_registration.binance import \
    BinanceCard2Wallet2CryptoExchangesParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# @app.task(bind=True, max_retries=None)
# def binance_card_2_crypto_exchanges(self):
#     try:
#         # group(
#         #     get_binance_card_2_crypto_exchanges.s(trade_type)
#         #     for trade_type in ('BUY', 'SELL')
#         # ).delay()
#         print('start')
#         get_tinkoff_p2p_binance_exchanges.apply()
#         print('stop')
#         self.retry(countdown=10)
#     except Exception as error:
#         logger.error(error)
#         self.retry()
#
# binance_card_2_crypto_exchanges.apply_async()


# @shared_task(bind=True)
# def my_task2(self):
#     try:
#         logger.info('Task started')
#         # Здесь ваш код задачи, который занимает 5 секунд
#         sleep(5)
#         logger.info('Task finished')
#     except Exception as exc:
#         logger.error('Возникло исключение: %s', exc)
#         raise exc
#     else:
#         # запуск задачи через 5 секунд после завершения
#         self.apply_async(countdown=5)
#
# @shared_task
# def my_repeating_task():
#     my_task2.apply_async(countdown=0)
#     logger.info('Задача запущена')

# @shared_task(bind=True, base=QueueOnce, once={'graceful': True, 'timeout': 60})
# def my_task(self):
#     lock_key = 'my_task_lock'
#     lock_expire = 10  # Время жизни блокировки в секундах
#     lock = self.app.connection().Lock(lock_key, expire=lock_expire)
#
#     if lock.acquire(blocking=False):
#         try:
#             logger.info('Task started')
#             # Здесь ваш код задачи, который занимает 5 секунд
#             sleep(5)
#             logger.info('Task finished')
#             self.apply_async(countdown=5)
#         except Exception as e:
#             logger.error(f'Task failed: {str(e)}')
#         finally:
#             lock.release()
#     else:
#         logger.info('Task is already running')

# @shared_task(bind=True, max_retries=3)
# def my_task(self):
#     try:
#         # ваш код для выполнения задачи
#         sleep(5)
#         if random.random() > 0.5:
#             raise Exception("Случайное исключение")
#         logger.info('Задача выполнена')
#     except Exception as exc:
#         logger.error('Возникло исключение: %s', exc)
#         if self.request.retries == self.max_retries:
#             logger.error('Превышен лимит повторов')
#             raise exc
#         self.retry(countdown=3)
#     else:
#         # запуск задачи через 2 минуты
#         self.apply_async(countdown=3)
#
#
# @shared_task
# def my_repeating_task():
#     my_task.apply_async(countdown=0)
#     logger.info('Задача запущена')


@app.task
def start_crypto_exchanges():
    info = InfoLoop.objects.filter(value=True).first()
    info.start_crypto_exchanges = datetime.now(timezone.utc)
    info.save()
    print('start_crypto_exchanges')


@app.task
def start_bank_exchanges():
    info = InfoLoop.objects.filter(value=True).first()
    info.start_banks_exchanges = datetime.now(timezone.utc)
    info.save()
    print('start_banks_exchanges')


@app.task
def end_all_exchanges(_):
    info = InfoLoop.objects.filter(value=True).first()
    duration = datetime.now(timezone.utc) - info.updated
    info.all_exchanges = duration
    count_of_rates = InterExchanges.objects.filter(update__updated__gte=(
            datetime.now(timezone.utc) - duration
    )).count()
    info.count_of_rates = count_of_rates
    info.save()
    print('end_all_exchanges')


@app.task
def end_crypto_exchanges(_):
    info = InfoLoop.objects.filter(value=True).first()
    duration = datetime.now(timezone.utc) - info.updated
    info.all_crypto_exchanges = duration
    info.save()
    print('end_crypto_exchanges')


@app.task
def end_banks_exchanges(_):
    info = InfoLoop.objects.filter(value=True).first()
    duration = datetime.now(timezone.utc) - info.updated
    info.all_banks_exchanges = duration
    info.save()
    print('end_banks_exchanges')


@app.task
def get_simpl_binance_tinkoff_inter_exchanges_calculate():
    simpl_binance_tinkoff_inter_exchanges_calculate = (
        SimplBinanceTinkoffInterExchangesCalculate()
    )
    simpl_binance_tinkoff_inter_exchanges_calculate.logger_start()
    simpl_binance_tinkoff_inter_exchanges_calculate.main()
    simpl_binance_tinkoff_inter_exchanges_calculate.logger_end()


@app.task
def get_simpl_binance_wise_inter_exchanges_calculate():
    simpl_binance_wise_inter_exchanges_calculate = (
        SimplBinanceWiseInterExchangesCalculate()
    )
    simpl_binance_wise_inter_exchanges_calculate.logger_start()
    simpl_binance_wise_inter_exchanges_calculate.main()
    simpl_binance_wise_inter_exchanges_calculate.logger_end()


@app.task
def get_complex_binance_tinkoff_inter_exchanges_calculate():
    complex_binance_tinkoff_inter_exchanges_calculate = (
        ComplexBinanceTinkoffInterExchangesCalculate()
    )
    complex_binance_tinkoff_inter_exchanges_calculate.logger_start()
    complex_binance_tinkoff_inter_exchanges_calculate.main()
    complex_binance_tinkoff_inter_exchanges_calculate.logger_end()


@app.task
def get_complex_binance_wise_inter_exchanges_calculate():
    complex_binance_wise_inter_exchanges_calculate = (
        ComplexBinanceWiseInterExchangesCalculate()
    )
    complex_binance_wise_inter_exchanges_calculate.logger_start()
    complex_binance_wise_inter_exchanges_calculate.main()
    complex_binance_wise_inter_exchanges_calculate.logger_end()


@app.task(queue='parsing')
def assets_loop():
    group(
        get_tinkoff_p2p_binance_exchanges.s(),
        get_wise_p2p_binance_exchanges.s(),
        get_all_binance_crypto_exchanges.s(),
        get_binance_card_2_crypto_exchanges_buy.s(),
        get_binance_card_2_crypto_exchanges_sell.s(),
        get_all_card_2_wallet_2_crypto_exchanges_buy.s(),
        get_all_card_2_wallet_2_crypto_exchanges_sell.s(),
        parse_internal_tinkoff_rates.s(),
        parse_internal_wise_rates.s()
    ).delay()


@app.task(queue='parsing')
def all_reg():
    all_registration()
