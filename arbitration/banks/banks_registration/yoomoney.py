import os

from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceP2PParser)
from crypto_exchanges.crypto_exchanges_registration.bybit import BybitP2PParser

BANK_NAME = os.path.basename(__file__).split('.')[0].capitalize()

YOOMONEY_CURRENCIES = (
    'USD', 'EUR', 'RUB', 'GBP', 'KZT', 'BYN',
)


class YoomoneyBinanceP2PParser(BinanceP2PParser):
    bank_name: str = BANK_NAME


class YoomoneyBybitP2PParser(BybitP2PParser):
    bank_name: str = BANK_NAME
