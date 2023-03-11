from datetime import datetime, timezone

from celery import group

from arbitration.celery import app
from arbitration.settings import (CARD_2_CRYPTO_BINANCE_UPDATE_FREQUENCY,
                                  EXCHANGES_BINANCE_UPDATE_FREQUENCY,
                                  UPDATE_RATE)
from banks.banks_config import BANKS_CONFIG
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceCard2CryptoExchangesParser,
    BinanceCard2Wallet2CryptoExchangesCalculating, BinanceCryptoParser,
    BinanceListsFiatCryptoParser, ComplexBinanceInterExchangesCalculating,
    ComplexBinanceInternationalInterExchangesCalculating,
    SimplBinanceInterExchangesCalculating,
    SimplBinanceInternationalInterExchangesCalculating)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_all_binance_crypto_exchanges(self):
    BinanceCryptoParser().main()
    self.retry(
        countdown=EXCHANGES_BINANCE_UPDATE_FREQUENCY * UPDATE_RATE[
            datetime.now(timezone.utc).hour
        ]
    )


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_binance_card_2_crypto_exchanges_buy(self):
    BinanceCard2CryptoExchangesParser('BUY').main()
    self.retry(
        countdown=CARD_2_CRYPTO_BINANCE_UPDATE_FREQUENCY * UPDATE_RATE[
            datetime.now(timezone.utc).hour
        ]
    )


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_binance_card_2_crypto_exchanges_sell(self):
    BinanceCard2CryptoExchangesParser('SELL').main()
    self.retry(
        countdown=CARD_2_CRYPTO_BINANCE_UPDATE_FREQUENCY * UPDATE_RATE[
            datetime.now(timezone.utc).hour
        ]
    )


@app.task(max_retries=2, queue='parsing', autoretry_for=(Exception,))
def get_start_binance_fiat_crypto_list():
    BinanceListsFiatCryptoParser().main()


# Calculating
@app.task
def get_binance_fiat_crypto_list():
    BinanceListsFiatCryptoParser().main()


@app.task
def get_all_card_2_wallet_2_crypto_exchanges_buy():
    BinanceCard2Wallet2CryptoExchangesCalculating('BUY').main()


@app.task
def get_all_card_2_wallet_2_crypto_exchanges_sell():
    BinanceCard2Wallet2CryptoExchangesCalculating('SELL').main()


# Inter exchanges calculating
@app.task(queue='calculating')
def simpl_binance_inter_exchanges_calculating(bank_name, full_update):
    SimplBinanceInterExchangesCalculating(bank_name, full_update).main()


@app.task
def get_simpl_binance_inter_exchanges_calculating(full_update):
    group(
        simpl_binance_inter_exchanges_calculating.s(
            bank_name, full_update
        )
        for bank_name, config in BANKS_CONFIG.items()
        if 'Binance' in config['crypto_exchanges']
    ).delay()


@app.task(queue='calculating')
def simpl_binance_international_inter_exchanges_calculating(
        bank_name, full_update
):
    SimplBinanceInternationalInterExchangesCalculating(
        bank_name, full_update
    ).main()


@app.task
def get_simpl_binance_international_inter_exchanges_calculating(full_update):
    group(
        simpl_binance_international_inter_exchanges_calculating.s(
            bank_name, full_update
        )
        for bank_name, config in BANKS_CONFIG.items()
        if 'Binance' in config['crypto_exchanges']
    ).delay()


@app.task(queue='calculating')
def complex_binance_inter_exchanges_calculating(bank_name, full_update):
    ComplexBinanceInterExchangesCalculating(bank_name, full_update).main()


@app.task
def get_complex_binance_inter_exchanges_calculating(full_update):
    group(
        complex_binance_inter_exchanges_calculating.s(
            bank_name, full_update
        )
        for bank_name, config in BANKS_CONFIG.items()
        if config['bank_parser']
    ).delay()


@app.task(queue='calculating')
def complex_binance_international_inter_exchanges_calculating(bank_name,
                                                              full_update):
    ComplexBinanceInternationalInterExchangesCalculating(bank_name,
                                                         full_update).main()


@app.task
def get_complex_binance_international_inter_exchanges_calculating(full_update):
    group(
        complex_binance_international_inter_exchanges_calculating.s(
            bank_name, full_update
        )
        for bank_name, config in BANKS_CONFIG.items()
        if config['bank_parser']
    ).delay()
