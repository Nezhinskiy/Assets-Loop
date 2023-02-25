import logging

from arbitration.celery import app
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceCard2CryptoExchangesParser,
    BinanceCard2Wallet2CryptoExchangesCalculate, BinanceCryptoParser,
    BinanceListsFiatCryptoParser, TinkoffBinanceP2PParser,
    WiseBinanceP2PParser)

logger = logging.getLogger(__name__)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_tinkoff_p2p_binance_exchanges(self):
    TinkoffBinanceP2PParser().main()
    self.retry(countdown=70)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_wise_p2p_binance_exchanges(self):
    WiseBinanceP2PParser().main()
    self.retry(countdown=70)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_all_binance_crypto_exchanges(self):
    BinanceCryptoParser().main()
    self.retry(countdown=75)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_binance_card_2_crypto_exchanges_buy(self):
    BinanceCard2CryptoExchangesParser('BUY').main()
    self.retry(countdown=170)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_binance_card_2_crypto_exchanges_sell(self):
    BinanceCard2CryptoExchangesParser('SELL').main()
    self.retry(countdown=170)


@app.task(max_retries=2, queue='parsing', autoretry_for=(Exception,))
def get_start_binance_fiat_crypto_list():
    BinanceListsFiatCryptoParser().main()


@app.task
def get_binance_fiat_crypto_list():
    BinanceListsFiatCryptoParser().main()


@app.task
def get_all_card_2_wallet_2_crypto_exchanges_buy():
    BinanceCard2Wallet2CryptoExchangesCalculate('BUY').main()


@app.task
def get_all_card_2_wallet_2_crypto_exchanges_sell():
    BinanceCard2Wallet2CryptoExchangesCalculate('SELL').main()
