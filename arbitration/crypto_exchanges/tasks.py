from datetime import datetime
from arbitration.celery import app
from dateutil import parser

from core.models import InfoLoop
from crypto_exchanges.crypto_exchanges_registration.binance import TinkoffBinanceP2PParser, WiseBinanceP2PParser, BinanceCryptoParser, \
    BinanceListsFiatCryptoParser, BinanceCard2CryptoExchangesParser, BinanceCard2Wallet2CryptoExchangesParser, \
    BinanceBestCryptoExchanges, BinanceBestTotalCryptoExchanges


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
def get_binance_card_2_crypto_exchanges():
    binance_fiat_crypto_list_parser = BinanceListsFiatCryptoParser()
    binance_fiat_crypto_list_parser.main()
    binance_card_2_crypto_exchanges_parser = BinanceCard2CryptoExchangesParser()
    binance_card_2_crypto_exchanges_parser.main()


@app.task
def get_all_card_2_wallet_2_crypto_exchanges(_):
    card_2_wallet_2_crypto_exchanges_parser = BinanceCard2Wallet2CryptoExchangesParser()
    card_2_wallet_2_crypto_exchanges_parser.main()


# Best crypto exchanges
@app.task
def best_crypto_exchanges_intra_exchanges(str_start_time):
    start_time = parser.parse(str_start_time[0])
    best_intra_crypto_exchanges = BinanceBestCryptoExchanges()
    best_intra_crypto_exchanges.main()
    best_intra_card_2_card_crypto_exchanges = BinanceBestTotalCryptoExchanges()
    best_intra_card_2_card_crypto_exchanges.main()
    print('crypto_exchanges_end')
    duration = datetime.now() - start_time
    new_loop = InfoLoop.objects.filter(value=True).last()
    new_loop.all_crypto_exchanges = duration
    new_loop.save()
