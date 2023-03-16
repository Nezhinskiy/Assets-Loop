from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceP2PParser)
from crypto_exchanges.crypto_exchanges_registration.bybit import BybitP2PParser

BANK_NAME = 'Bank of Georgia'

BOG_CURRENCIES = (
    'USD', 'EUR', 'GEL', 'GBP'
)


class BOGBinanceP2PParser(BinanceP2PParser):
    bank_name: str = BANK_NAME


class BOGBybitP2PParser(BybitP2PParser):
    bank_name: str = BANK_NAME
