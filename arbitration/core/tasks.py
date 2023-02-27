import logging
from datetime import datetime, timezone

from celery import group
from arbitration.celery import app
from banks.tasks import (
                         parse_currency_market_tinkoff_rates,
                         parse_internal_tinkoff_rates,
                         parse_internal_wise_rates,
                         parse_internal_raiffeisen_rates,
)
from core.registration import all_registration
from crypto_exchanges.tasks import (
                                    get_all_binance_crypto_exchanges,
                                    get_all_card_2_wallet_2_crypto_exchanges_buy,
                                    get_all_card_2_wallet_2_crypto_exchanges_sell,
                                    get_binance_card_2_crypto_exchanges_buy,
                                    get_binance_card_2_crypto_exchanges_sell,
                                    get_start_binance_fiat_crypto_list
                                    )

from core.models import InfoLoop

from arbitration.settings import PARSING_WORKER_NAME

from banks.tasks import get_tinkoff_p2p_binance_exchanges, get_wise_p2p_binance_exchanges, get_sberbank_p2p_binance_exchanges, get_raiffeisen_p2p_binance_exchanges, get_qiwi_p2p_binance_exchanges

from banks.banks_config import BANKS_CONFIG
from crypto_exchanges.crypto_exchanges_registration.binance import \
    SimplBinanceInterExchangesCalculating, \
    ComplexBinanceInterExchangesCalculating

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.task(queue='parsing')
def all_reg():
    all_registration()
    get_start_binance_fiat_crypto_list.s().delay()


@app.task(bind=True, max_retries=4, queue='parsing')
def delete_tasks_wait_for_idle(self):
    app.control.purge()
    stats = app.control.inspect().stats().get(PARSING_WORKER_NAME)
    try:
        active_tasks = (
            stats.get('pool').get('writes').get('inqueues').get('active')
        )
        if active_tasks > 0:
            logger.info(f'Есть активные задачи: {active_tasks}')
            app.control.wait_for_workers([PARSING_WORKER_NAME], 90, force=True)
        app.control.purge()
        new_stats = app.control.inspect().stats().get(PARSING_WORKER_NAME)
        new_active_tasks = (
            new_stats.get('pool').get('writes').get('inqueues').get('active')
        )
        if new_active_tasks > 0:
            self.retry()
        logger.info('Все задачи удалены из очереди')
    except Exception as error:
        logger.info(stats)
        message = f'Нет доступной статистики по воркерам: {error}'
        logger.error(message)
        raise Exception


@app.task(queue='parsing')
def assets_loop_stop():
    # delete_tasks_wait_for_idle.s().apply()
    try:
        target_loop = InfoLoop.objects.first()
        target_loop.value = False
        datetime_now = datetime.now(timezone.utc)
        target_loop.stopped = datetime_now
        target_loop.duration = datetime_now - target_loop.started
        target_loop.save()
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task(queue='parsing')
def assets_loop():
    # get_start_binance_fiat_crypto_list.s().apply()
    group(
        get_tinkoff_p2p_binance_exchanges.s(),
        get_raiffeisen_p2p_binance_exchanges.s(),
        get_wise_p2p_binance_exchanges.s(),
        get_sberbank_p2p_binance_exchanges.s(),
        get_all_binance_crypto_exchanges.s(),
        get_binance_card_2_crypto_exchanges_buy.s(),
        get_binance_card_2_crypto_exchanges_sell.s(),
        parse_internal_tinkoff_rates.s(),
        parse_internal_raiffeisen_rates.s(),
        get_qiwi_p2p_binance_exchanges.s(),
        parse_internal_wise_rates.s()
    ).delay()


# Inter exchanges calculating
@app.task(queue='calculating')
def simpl_binance_inter_exchanges_calculating(bank_name):
    SimplBinanceInterExchangesCalculating(bank_name).main()


@app.task
def get_simpl_binance_inter_exchanges_calculating():
    group(
        simpl_binance_inter_exchanges_calculating.s(bank_name)
        for bank_name, config in BANKS_CONFIG.items()
        if 'Binance' in config['crypto_exchanges']
    ).delay()


@app.task(queue='calculating')
def complex_binance_inter_exchanges_calculating(bank_name):
    ComplexBinanceInterExchangesCalculating(bank_name).main()


@app.task
def get_complex_binance_inter_exchanges_calculating():
    group(
        complex_binance_inter_exchanges_calculating.s(bank_name)
        for bank_name, config in BANKS_CONFIG.items()
        if config['bank_parser']
    ).delay()
