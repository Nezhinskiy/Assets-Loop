import os

from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceP2PParser)
from crypto_exchanges.crypto_exchanges_registration.bybit import BybitP2PParser

BANK_NAME = os.path.basename(__file__).split('.')[0].upper()

TBC_CURRENCIES = (
    'USD', 'EUR', 'GEL', 'GBP'
)


class TBCBinanceP2PParser(BinanceP2PParser):
    bank_name: str = BANK_NAME


class TBCBybitP2PParser(BybitP2PParser):
    bank_name: str = BANK_NAME
