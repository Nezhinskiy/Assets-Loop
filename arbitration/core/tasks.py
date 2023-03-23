import logging
from datetime import datetime, timezone

from celery import group

from arbitration.celery import app
from arbitration.settings import PARSING_WORKER_NAME
from banks.banks_config import BANKS_CONFIG
from banks.tasks import (get_bog_p2p_binance_exchanges,
                         get_bog_p2p_bybit_exchanges,
                         get_credo_p2p_binance_exchanges,
                         get_credo_p2p_bybit_exchanges,
                         get_qiwi_p2p_binance_exchanges,
                         get_qiwi_p2p_bybit_exchanges,
                         get_raiffeisen_p2p_binance_exchanges,
                         get_raiffeisen_p2p_bybit_exchanges,
                         get_sberbank_p2p_binance_exchanges,
                         get_sberbank_p2p_bybit_exchanges,
                         get_tbc_p2p_binance_exchanges,
                         get_tbc_p2p_bybit_exchanges,
                         get_tinkoff_p2p_binance_exchanges,
                         get_tinkoff_p2p_bybit_exchanges,
                         get_wise_p2p_binance_exchanges,
                         get_wise_p2p_bybit_exchanges,
                         get_yoomoney_p2p_binance_exchanges,
                         get_yoomoney_p2p_bybit_exchanges,
                         parse_internal_raiffeisen_rates,
                         parse_internal_tinkoff_rates,
                         parse_internal_wise_rates)
from core.calculations import (ComplexInterExchangesCalculating,
                               ComplexInternationalInterExchangesCalculating,
                               SimplInterExchangesCalculating,
                               SimplInternationalInterExchangesCalculating)
from core.models import InfoLoop
from core.registration import all_registration
from crypto_exchanges.models import InterExchangesUpdates
from crypto_exchanges.tasks import (get_all_binance_crypto_exchanges,
                                    get_all_bybit_crypto_exchanges,
                                    get_binance_card_2_crypto_exchanges_buy,
                                    get_binance_card_2_crypto_exchanges_sell,
                                    get_start_binance_fiat_crypto_list)

logger = logging.getLogger(__name__)


@app.task(queue='parsing')
def all_reg():
    all_registration()
    get_start_binance_fiat_crypto_list.s().apply()
    logger.error('Finish registration')


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
    try:
        InterExchangesUpdates.objects.filter(ended=False).delete()
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
    group(
        get_all_binance_crypto_exchanges.s(),
        get_all_bybit_crypto_exchanges.s(),
        get_tinkoff_p2p_binance_exchanges.s(),
        get_sberbank_p2p_binance_exchanges.s(),
        get_raiffeisen_p2p_binance_exchanges.s(),
        get_qiwi_p2p_binance_exchanges.s(),
        get_yoomoney_p2p_binance_exchanges.s(),
        get_bog_p2p_binance_exchanges.s(),
        get_tbc_p2p_binance_exchanges.s(),
        get_credo_p2p_binance_exchanges.s(),
        get_wise_p2p_binance_exchanges.s(),
        get_tinkoff_p2p_bybit_exchanges.s(),
        get_sberbank_p2p_bybit_exchanges.s(),
        get_raiffeisen_p2p_bybit_exchanges.s(),
        get_qiwi_p2p_bybit_exchanges.s(),
        get_yoomoney_p2p_bybit_exchanges.s(),
        get_bog_p2p_bybit_exchanges.s(),
        get_tbc_p2p_bybit_exchanges.s(),
        get_credo_p2p_bybit_exchanges.s(),
        get_wise_p2p_bybit_exchanges.s(),
        parse_internal_tinkoff_rates.s(),
        parse_internal_raiffeisen_rates.s(),
        parse_internal_wise_rates.s(),
        get_binance_card_2_crypto_exchanges_buy.s(),
        get_binance_card_2_crypto_exchanges_sell.s(),
    ).delay()


# Inter exchanges calculating
@app.task(queue='calculating')
def simpl_inter_exchanges_calculating(
        crypto_exchange_name, bank_name, full_update):
    SimplInterExchangesCalculating(
        crypto_exchange_name, bank_name, full_update).main()


@app.task
def get_simpl_inter_exchanges_calculating(full_update):
    from crypto_exchanges.crypto_exchanges_config import (
        CRYPTO_EXCHANGES_CONFIG)
    group(
        simpl_inter_exchanges_calculating.s(
            crypto_exchange_name, bank_name, full_update
        ) for crypto_exchange_name in CRYPTO_EXCHANGES_CONFIG.keys()
        for bank_name, config in BANKS_CONFIG.items()
        if 'Binance' in config['crypto_exchanges']
    ).delay()


@app.task(queue='calculating')
def simpl_international_inter_exchanges_calculating(
        crypto_exchange_name, bank_name, full_update):
    SimplInternationalInterExchangesCalculating(
        crypto_exchange_name, bank_name, full_update).main()


@app.task
def get_simpl_international_inter_exchanges_calculating(full_update):
    from crypto_exchanges.crypto_exchanges_config import (
        CRYPTO_EXCHANGES_CONFIG)
    group(
        simpl_international_inter_exchanges_calculating.s(
            crypto_exchange_name, bank_name, full_update
        ) for crypto_exchange_name in CRYPTO_EXCHANGES_CONFIG.keys()
        for bank_name, config in BANKS_CONFIG.items()
        if 'Binance' in config['crypto_exchanges']
    ).delay()


@app.task(queue='calculating')
def complex_inter_exchanges_calculating(
        crypto_exchange_name, bank_name, full_update):
    ComplexInterExchangesCalculating(
        crypto_exchange_name, bank_name, full_update).main()


@app.task
def get_complex_inter_exchanges_calculating(full_update):
    from crypto_exchanges.crypto_exchanges_config import (
        CRYPTO_EXCHANGES_CONFIG)
    group(
        complex_inter_exchanges_calculating.s(
            crypto_exchange_name, bank_name, full_update
        ) for crypto_exchange_name in CRYPTO_EXCHANGES_CONFIG.keys()
        for bank_name, config in BANKS_CONFIG.items()
        if config['bank_parser']
    ).delay()


@app.task(queue='calculating')
def complex_international_inter_exchanges_calculating(
        crypto_exchange_name, bank_name, full_update):
    ComplexInternationalInterExchangesCalculating(
        crypto_exchange_name, bank_name, full_update).main()


@app.task
def get_complex_international_inter_exchanges_calculating(full_update):
    from crypto_exchanges.crypto_exchanges_config import (
        CRYPTO_EXCHANGES_CONFIG)
    group(
        complex_international_inter_exchanges_calculating.s(
            crypto_exchange_name, bank_name, full_update
        ) for crypto_exchange_name in CRYPTO_EXCHANGES_CONFIG.keys()
        for bank_name, config in BANKS_CONFIG.items()
        if config['bank_parser']
    ).delay()
