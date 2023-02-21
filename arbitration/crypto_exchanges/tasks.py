import logging
from datetime import datetime

from celery import group
from dateutil import parser

from arbitration.celery import app
from core.models import InfoLoop
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceCard2CryptoExchangesParser,
    BinanceCard2Wallet2CryptoExchangesParser, BinanceCryptoParser,
    BinanceListsFiatCryptoParser, TinkoffBinanceP2PParser,
    WiseBinanceP2PParser)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Crypto exchanges time
@app.task
def crypto_exchanges_start_time():
    print('banks_start')
    return datetime.now()


tinkoff_p2p_binance_exchanges = TinkoffBinanceP2PParser()
wise_p2p_binance_exchanges = WiseBinanceP2PParser()
binance_crypto_exchanges = BinanceCryptoParser()
binance_card_2_crypto_exchanges_buy = BinanceCard2CryptoExchangesParser('BUY')
binance_card_2_crypto_exchanges_sell = (
    BinanceCard2CryptoExchangesParser('SELL'))
card_2_wallet_2_crypto_exchanges_buy = (
        BinanceCard2Wallet2CryptoExchangesParser('BUY'))
card_2_wallet_2_crypto_exchanges_sell = (
        BinanceCard2Wallet2CryptoExchangesParser('SELL'))


@app.task(bind=True, max_retries=None)
def get_tinkoff_p2p_binance_exchanges(self):
    tinkoff_p2p_binance_exchanges.logger_start()
    tinkoff_p2p_binance_exchanges.main()
    tinkoff_p2p_binance_exchanges.logger_end()
    self.retry(countdown=70)


@app.task(bind=True, max_retries=None)
def get_wise_p2p_binance_exchanges(self):
    wise_p2p_binance_exchanges.logger_start()
    wise_p2p_binance_exchanges.main()
    wise_p2p_binance_exchanges.logger_end()
    self.retry(countdown=70)


@app.task(bind=True, max_retries=None)
def get_all_binance_crypto_exchanges(self):
    binance_crypto_exchanges.logger_start()
    binance_crypto_exchanges.main()
    binance_crypto_exchanges.logger_end()
    self.retry(countdown=75)


@app.task(bind=True, max_retries=None)
def get_binance_card_2_crypto_exchanges_buy(self):
    binance_card_2_crypto_exchanges_buy.logger_start()
    binance_card_2_crypto_exchanges_buy.main()
    binance_card_2_crypto_exchanges_buy.logger_end()
    self.retry(countdown=170)


@app.task(bind=True, max_retries=None)
def get_binance_card_2_crypto_exchanges_sell(self):
    binance_card_2_crypto_exchanges_sell.logger_start()
    binance_card_2_crypto_exchanges_sell.main()
    binance_card_2_crypto_exchanges_sell.logger_end()
    self.retry(countdown=170)


@app.task
def get_binance_fiat_crypto_list():
    BinanceListsFiatCryptoParser().main()


@app.task(bind=True, max_retries=None)
def get_all_card_2_wallet_2_crypto_exchanges_buy(self):
    card_2_wallet_2_crypto_exchanges_buy.logger_start()
    card_2_wallet_2_crypto_exchanges_buy.main()
    card_2_wallet_2_crypto_exchanges_buy.logger_end()
    self.retry(countdown=55)


@app.task(bind=True, max_retries=None)
def get_all_card_2_wallet_2_crypto_exchanges_sell(self):
    card_2_wallet_2_crypto_exchanges_sell.logger_start()
    card_2_wallet_2_crypto_exchanges_sell.main()
    card_2_wallet_2_crypto_exchanges_sell.logger_end()
    self.retry(countdown=55)



# group(
#     # get_tinkoff_p2p_binance_exchanges.s(),
#     # get_wise_p2p_binance_exchanges.s(),
#     # get_all_binance_crypto_exchanges.s(),
#     # get_binance_card_2_crypto_exchanges_buy.s(),
#     # get_binance_card_2_crypto_exchanges_sell.s(),
#     get_all_card_2_wallet_2_crypto_exchanges_buy.s(),
#     get_all_card_2_wallet_2_crypto_exchanges_sell.s()
# ).delay()

# get_all_card_2_wallet_2_crypto_exchanges_buy.apply()