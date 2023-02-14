import re
import socket
import subprocess
from datetime import datetime, timezone
from time import sleep

import docker
from celery import chord, group
from dateutil import parser

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
from crypto_exchanges.tasks import (best_crypto_exchanges_intra_exchanges,
                                    crypto_exchanges_start_time,
                                    get_all_binance_crypto_exchanges,
                                    get_all_card_2_wallet_2_crypto_exchanges,
                                    get_binance_card_2_crypto_exchanges,
                                    get_tinkoff_p2p_binance_exchanges,
                                    get_wise_p2p_binance_exchanges
                                    )

import socks
from fake_useragent import UserAgent
from stem.control import Controller
from stem import Signal
import requests


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
        get_binance_card_2_crypto_exchanges.s(trade_type)
        for trade_type in ('BUY', 'SELL')
    )
    group_all_banks_binance_crypto_exchanges = group(
        chord(
            get_all_binance_crypto_exchanges.s(),
            get_all_card_2_wallet_2_crypto_exchanges.s()
        ), group_binance_card_2_crypto_exchanges
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
    general_chord = chord(general_group,
                          end_all_exchanges.s())
    if InfoLoop.objects.last().value == 0:
        InfoLoop.objects.create(value=True)
        count_loop = 0
        while InfoLoop.objects.last().value == 1:
            general_chord.delay()
            while (InfoLoop.objects.last().value == 1
                    and not InfoLoop.objects.last().all_exchanges):
                sleep(5)
            if (
                    InfoLoop.objects.last().all_crypto_exchanges
                    and InfoLoop.objects.last().all_banks_exchanges
            ):
                count_loop += 1
                print(count_loop)
                if count_loop >= 100:
                    if InfoLoop.objects.last().value == 1:
                        InfoLoop.objects.create(value=False)
                else:
                    sleep(5)
                    # if count_loop == 1:
                    #     sleep(60)
                    # else:
                    #     sleep(120)
                    InfoLoop.objects.create(value=True)
            else:
                if InfoLoop.objects.last().value == 1:
                    InfoLoop.objects.create(value=False)


@app.task
def all_reg():
    all_registration()


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