import os

from arbitration.settings import API_WISE
from core.parsers import BankParser
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceP2PParser)
from crypto_exchanges.crypto_exchanges_registration.bybit import BybitP2PParser

BANK_NAME = os.path.basename(__file__).split('.')[0].capitalize()

WISE_CURRENCIES = (
    'USD', 'EUR', 'UAH', 'ILS', 'GBP', 'GEL', 'TRY', 'CHF', 'AUD'
)  # 'CZK', 'RON', 'NZD', 'AED', 'CLP', 'INR', 'SGD', 'HUF', 'PLN', 'CAD',
# 'CHF', 'AUD', 'CNY', 'JPY'


class WiseParser(BankParser):
    bank_name: str = BANK_NAME
    endpoint: str = API_WISE
    name_from: str = 'sourceCurrency'
    name_to: str = 'targetCurrency'
    buy_and_sell: bool = False
    # custom_settings
    source_amount: int = 10000
    profile_country: str = 'RU'
    connection_type: str = 'Tor'
    need_cookies: bool = False

    def _create_params(self, fiats_combinations):
        params = [dict([('sourceAmount', self.source_amount),
                        (self.name_from, params[0]),
                        (self.name_to, params[-1]),
                        ('profileCountry', self.profile_country)])
                  for params in fiats_combinations]
        return params

    def _extract_price_from_json(self, json_data: list) -> float:
        if json_data and len(json_data) > 1:
            for exchange_data in json_data:
                pay_in_method = exchange_data.get('payInMethod')
                pay_out_method = exchange_data.get('payOutMethod')
                if pay_in_method == pay_out_method == 'BALANCE':
                    price_before_commission = exchange_data.get('midRate')
                    fee = exchange_data.get('total')
                    commission = fee / self.source_amount * 100
                    price = price_before_commission * 100 / (100 + commission)
                    return price


class WiseBinanceP2PParser(BinanceP2PParser):
    bank_name: str = BANK_NAME


class WiseBybitP2PParser(BybitP2PParser):
    bank_name: str = BANK_NAME
