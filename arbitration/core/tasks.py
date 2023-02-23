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


@app.task
def assets_loop():
    # 1. Crypto exchanges
    # 1.1 Binance
    # 1.1.1 Tinkoff

    group_tinkoff_inter_exchanges_calculate = group(
        get_complex_binance_tinkoff_inter_exchanges_calculate.s(),
        get_simpl_binance_tinkoff_inter_exchanges_calculate.s()
    )
    group_tinkoff_binance_p2p = group(get_tinkoff_p2p_binance_exchanges.s())
    chord_tinkoff_binance_p2p = chord(
        group_tinkoff_binance_p2p,
        get_simpl_binance_tinkoff_inter_exchanges_calculate.s()
    )
    # 1.1.2 Wise
    group_wise_inter_exchanges_calculate = group(
        get_complex_binance_wise_inter_exchanges_calculate.s(),
        get_simpl_binance_wise_inter_exchanges_calculate.s()
    )
    group_wise_binance_p2p = group(get_wise_p2p_binance_exchanges.s())
    chord_wise_binance_p2p = chord(
        group_wise_binance_p2p,
        get_simpl_binance_wise_inter_exchanges_calculate.s()
    )
    # 1.0 All banks
    group_all_bank_complex_inter_exchanges_calculate = group(
        get_complex_binance_tinkoff_inter_exchanges_calculate.s(),
        get_complex_binance_wise_inter_exchanges_calculate.s(),
    )
    group_all_banks_inter_exchanges_calculate = group(
        group_tinkoff_inter_exchanges_calculate,
        group_wise_inter_exchanges_calculate
    )
    group_binance_card_2_crypto_exchanges = group(
        get_binance_card_2_crypto_exchanges_buy,
        get_binance_card_2_crypto_exchanges_sell
    )
    group_card_2_wallet_2_crypto_exchanges = group(
        get_all_card_2_wallet_2_crypto_exchanges_buy,
        get_all_card_2_wallet_2_crypto_exchanges_sell
    )
    group_all_banks_binance_crypto_exchanges = group(
        get_all_binance_crypto_exchanges.s(),
        group_card_2_wallet_2_crypto_exchanges,
        group_binance_card_2_crypto_exchanges
    )
    chord_binance_crypto_exchanges = chord(
        group_all_banks_binance_crypto_exchanges,
        group_all_banks_inter_exchanges_calculate
    )

    # 2. Banks
    # 2.1 Tinkoff
    group_tinkoff_rates = group(parse_internal_tinkoff_rates.s(),
                                parse_currency_market_tinkoff_rates.s())
    chord_tinkoff_rates = chord(
        group_tinkoff_rates,
        get_simpl_binance_tinkoff_inter_exchanges_calculate.s()
    )
    # 2.2 Wise
    group_wise_rates = group(parse_internal_wise_rates.s())
    chord_wise_rates = chord(
        group_wise_rates, get_simpl_binance_wise_inter_exchanges_calculate.s()
    )

    # General
    # 0.1 Crypto exchanges
    general_group_crypto_exchanges = group(
        chord_tinkoff_binance_p2p, chord_wise_binance_p2p,
        chord_binance_crypto_exchanges
    )
    general_chord_crypto_exchanges = chord(chord(
        general_group_crypto_exchanges,
        group_all_bank_complex_inter_exchanges_calculate
    ), end_crypto_exchanges.s())
    # 0.2 Banks
    general_group_banks_exchanges = group(
        chord_tinkoff_rates, chord_wise_rates
    )
    general_chord_banks_exchanges = chord(chord(
        general_group_banks_exchanges,
        group_all_bank_complex_inter_exchanges_calculate
    ), end_banks_exchanges.s())
    # 0.
    general_group = group(
        general_chord_crypto_exchanges, general_chord_banks_exchanges
    )
    general_chord = chord(general_group, end_all_exchanges.s())
    if not InfoLoop.objects.first().value:
        InfoLoop.objects.create(value=True)
        count_loop = 0
        while InfoLoop.objects.first().value == 1:
            general_chord.delay()
            while (InfoLoop.objects.first().value
                   and not InfoLoop.objects.first().all_exchanges):
                sleep(1)
            if (InfoLoop.objects.filter(value=True
                                        ).first().all_crypto_exchanges
                    and InfoLoop.objects.filter(value=True
                                                ).first().all_banks_exchanges):
                count_loop += 1
                print(count_loop)
                if count_loop >= 1000:
                    if InfoLoop.objects.first().value:
                        InfoLoop.objects.create(value=False)
                else:
                    InfoLoop.objects.create(value=True)
                    # app.control.purge()
            else:
                if InfoLoop.objects.first().value:
                    InfoLoop.objects.create(value=False)


@app.task(bind=True, max_retries=None, queue='parsing')
def all_reg(self):
    # get_tinkoff_p2p_binance_exchanges.delay()
    # get_wise_p2p_binance_exchanges.delay(),
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
    # self.retry(countdown=17)
    # all_registration()


@app.task
def torr(a):
    err = 0
    counter = 0
    url = "https://httpbin.org/user-agent"

    def get_tor_session():
        # инициализировать сеанс запросов
        session = requests.Session()
        # установка прокси для http и https на localhost: 9050
        # для этого требуется запущенная служба Tor на вашем компьютере и прослушивание порта 9050 (по умолчанию)
        session.proxies = {"http": "socks5://tor_proxy:9050",
                           "https": "socks5://tor_proxy:9050"}
        session.headers = {'User-Agent': UserAgent().chrome}
        return session

    def get_container_ip():
        container_name = "infra_tor_proxy_1"
        cmd = "ping -c 1 " + container_name
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        return re.findall(r'\(.*?\)', output)[0][1:-1]

    def renew_connection():
        with Controller.from_port(address=get_container_ip()) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)
            sleep(c.get_newnym_wait())

    s = get_tor_session()
    while counter < 150:
        r = s.get(url)
        print(r.text)
        counter = counter + 1
        if a == 2:
            if counter % 5 == 0:
                # renew_connection()
                s = get_tor_session()
        # renew_connection()
        #wait till next identity will be available
    return print("Used " + str(counter) + " IPs and got " + str(err) + " errors")


@app.task
def tor():
    tor_group = group(torr.s(1), torr.s(2))
    tor_group.delay()


@app.task
def notor():
    err = 0
    counter = 0
    url = "https://httpbin.org/ip"
    session = requests.Session()
    while counter < 10:
        r = session.get(url)
        print(r.text)
        counter = counter + 1
        #wait till next identity will be available
    return print("Used " + str(counter) + " IPs and got " + str(err) + " errors")


@app.task
def c2c_s():
    get_binance_card_2_crypto_exchanges.s('SELL').delay()


@app.task
def c2c_b():
    get_binance_card_2_crypto_exchanges.s('BUY').delay()
