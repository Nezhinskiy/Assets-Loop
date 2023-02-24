import logging

from arbitration.celery import app
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceCard2CryptoExchangesParser,
    BinanceCard2Wallet2CryptoExchangesParser, BinanceCryptoParser,
    BinanceListsFiatCryptoParser, TinkoffBinanceP2PParser,
    WiseBinanceP2PParser)

logger = logging.getLogger(__name__)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_tinkoff_p2p_binance_exchanges(self):
    tinkoff_p2p_binance_exchanges = TinkoffBinanceP2PParser()
    try:
        tinkoff_p2p_binance_exchanges.logger_start()
        tinkoff_p2p_binance_exchanges.main()
        tinkoff_p2p_binance_exchanges.logger_end()
        self.retry(countdown=70)
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_wise_p2p_binance_exchanges(self):
    wise_p2p_binance_exchanges = WiseBinanceP2PParser()
    try:
        wise_p2p_binance_exchanges.logger_start()
        wise_p2p_binance_exchanges.main()
        wise_p2p_binance_exchanges.logger_end()
        self.retry(countdown=70)
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_all_binance_crypto_exchanges(self):
    binance_crypto_exchanges = BinanceCryptoParser()
    try:
        binance_crypto_exchanges.logger_start()
        binance_crypto_exchanges.main()
        binance_crypto_exchanges.logger_end()
        self.retry(countdown=75)
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_binance_card_2_crypto_exchanges_buy(self):
    binance_card_2_crypto_exchanges_buy = BinanceCard2CryptoExchangesParser(
        'BUY')
    try:
        binance_card_2_crypto_exchanges_buy.logger_start()
        binance_card_2_crypto_exchanges_buy.main()
        binance_card_2_crypto_exchanges_buy.logger_end()
        self.retry(countdown=170)
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_binance_card_2_crypto_exchanges_sell(self):
    binance_card_2_crypto_exchanges_sell = (
        BinanceCard2CryptoExchangesParser('SELL'))
    try:
        binance_card_2_crypto_exchanges_sell.logger_start()
        binance_card_2_crypto_exchanges_sell.main()
        binance_card_2_crypto_exchanges_sell.logger_end()
        self.retry(countdown=170)
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_all_card_2_wallet_2_crypto_exchanges_buy(self):
    card_2_wallet_2_crypto_exchanges_buy = (
        BinanceCard2Wallet2CryptoExchangesParser('BUY'))
    try:
        card_2_wallet_2_crypto_exchanges_buy.logger_start()
        card_2_wallet_2_crypto_exchanges_buy.main()
        card_2_wallet_2_crypto_exchanges_buy.logger_end()
        self.retry(countdown=55)
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_all_card_2_wallet_2_crypto_exchanges_sell(self):
    card_2_wallet_2_crypto_exchanges_sell = (
        BinanceCard2Wallet2CryptoExchangesParser('SELL'))
    try:
        card_2_wallet_2_crypto_exchanges_sell.logger_start()
        card_2_wallet_2_crypto_exchanges_sell.main()
        card_2_wallet_2_crypto_exchanges_sell.logger_end()
        self.retry(countdown=55)
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task(max_retries=2, queue='parsing', autoretry_for=(Exception,))
def get_start_binance_fiat_crypto_list():
    binance_fiat_crypto_list = BinanceListsFiatCryptoParser()
    try:
        binance_fiat_crypto_list.logger_start()
        binance_fiat_crypto_list.main()
        binance_fiat_crypto_list.logger_end()
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task
def get_binance_fiat_crypto_list():
    binance_fiat_crypto_list = BinanceListsFiatCryptoParser()
    try:
        binance_fiat_crypto_list.logger_start()
        binance_fiat_crypto_list.main()
        binance_fiat_crypto_list.logger_end()
    except Exception as error:
        logger.error(error)
        raise Exception
