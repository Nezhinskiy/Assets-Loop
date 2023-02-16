from datetime import datetime

from dateutil import parser

from arbitration.celery import app
from core.models import InfoLoop
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceCard2CryptoExchangesParser,
    BinanceCard2Wallet2CryptoExchangesParser, BinanceCryptoParser,
    BinanceListsFiatCryptoParser, TinkoffBinanceP2PParser,
    WiseBinanceP2PParser)


# Crypto exchanges time
@app.task
def crypto_exchanges_start_time():
    print('banks_start')
    return datetime.now()


@app.task
def get_tinkoff_p2p_binance_exchanges():
    binance_parser = TinkoffBinanceP2PParser()
    binance_parser.main()


@app.task
def get_wise_p2p_binance_exchanges():
    binance_parser = WiseBinanceP2PParser()
    binance_parser.main()


@app.task
def get_all_binance_crypto_exchanges():
    binance_crypto_parser = BinanceCryptoParser()
    binance_crypto_parser.main()


@app.task
def get_binance_card_2_crypto_exchanges(trade_type):
    # binance_fiat_crypto_list_parser = BinanceListsFiatCryptoParser()
    # binance_fiat_crypto_list_parser.main()
    binance_card_2_crypto_exchanges_parser = BinanceCard2CryptoExchangesParser(
        trade_type)
    binance_card_2_crypto_exchanges_parser.main()


@app.task
def get_all_card_2_wallet_2_crypto_exchanges(trade_type):
    card_2_wallet_2_crypto_exchanges_parser = (
        BinanceCard2Wallet2CryptoExchangesParser(trade_type))
    print('get_all_card_2_wallet_2_crypto_exchanges')
    card_2_wallet_2_crypto_exchanges_parser.main()


# Best crypto exchanges
@app.task
def best_crypto_exchanges_intra_exchanges(str_start_time):
    start_time = parser.parse(str_start_time[0])
    print('crypto_exchanges_end')
    duration = datetime.now() - start_time
    new_loop = InfoLoop.objects.filter(value=True).last()
    new_loop.all_crypto_exchanges = duration
    new_loop.save()
