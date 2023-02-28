import os

from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceP2PParser)

BANK_NAME = os.path.basename(__file__).split('.')[0].capitalize()

SBERBANK_CURRENCIES = (
    'USD', 'EUR', 'RUB', 'GBP', 'CHF', 'CAD', 'SGD', 'DKK',
    'NOK', 'SEK', 'JPY'
)


class SberbankBinanceP2PParser(BinanceP2PParser):
    bank_name: str = BANK_NAME
