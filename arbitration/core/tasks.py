from datetime import datetime, timezone
from time import sleep

from arbitration.celery import app
from celery import group, chord
from dateutil import parser
from core.models import InfoLoop
from banks.tasks import parse_internal_tinkoff_rates, parse_internal_wise_rates, parse_currency_market_tinkoff_rates, best_bank_intra_exchanges
from crypto_exchanges.tasks import crypto_exchanges_start_time, get_tinkoff_p2p_binance_exchanges, get_wise_p2p_binance_exchanges, get_all_binance_crypto_exchanges, get_binance_card_2_crypto_exchanges, get_all_card_2_wallet_2_crypto_exchanges, best_crypto_exchanges_intra_exchanges


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
    group_all_banks_binance_crypto_exchanges = group(
        chord(
            get_all_binance_crypto_exchanges.s(),
            get_all_card_2_wallet_2_crypto_exchanges.s()
        ), get_binance_card_2_crypto_exchanges.s()
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
                if count_loop >= 5:
                    if InfoLoop.objects.last().value == 1:
                        InfoLoop.objects.create(value=False)
                else:
                    if count_loop == 1:
                        sleep(60)
                    else:
                        sleep(120)
                    InfoLoop.objects.create(value=True)
            else:
                if InfoLoop.objects.last().value == 1:
                    InfoLoop.objects.create(value=False)
