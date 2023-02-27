import logging
from datetime import datetime, timezone

from arbitration.celery import app
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceCard2CryptoExchangesParser,
    BinanceCard2Wallet2CryptoExchangesCalculating, BinanceCryptoParser,
    BinanceListsFiatCryptoParser)

from arbitration.settings import UPDATE_RATE

logger = logging.getLogger(__name__)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_all_binance_crypto_exchanges(self):
    BinanceCryptoParser().main()
    self.retry(countdown=75 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_binance_card_2_crypto_exchanges_buy(self):
    BinanceCard2CryptoExchangesParser('BUY').main()
    self.retry(countdown=170 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_binance_card_2_crypto_exchanges_sell(self):
    BinanceCard2CryptoExchangesParser('SELL').main()
    self.retry(countdown=170 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(max_retries=2, queue='parsing', autoretry_for=(Exception,))
def get_start_binance_fiat_crypto_list():
    BinanceListsFiatCryptoParser().main()


@app.task
def get_binance_fiat_crypto_list():
    BinanceListsFiatCryptoParser().main()


@app.task
def get_all_card_2_wallet_2_crypto_exchanges_buy():
    BinanceCard2Wallet2CryptoExchangesCalculating('BUY').main()


@app.task
def get_all_card_2_wallet_2_crypto_exchanges_sell():
    BinanceCard2Wallet2CryptoExchangesCalculating('SELL').main()
