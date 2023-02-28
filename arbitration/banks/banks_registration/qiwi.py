import os

from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceP2PParser)

BANK_NAME = os.path.basename(__file__).split('.')[0].upper()

QIWI_CURRENCIES = (
    'USD', 'EUR', 'RUB', 'GBP', 'KZT'
)


class QIWIBinanceP2PParser(BinanceP2PParser):
    bank_name: str = BANK_NAME
