import os

from arbitration.settings import API_TINKOFF
from core.parsers import BankParser
from crypto_exchanges.crypto_exchanges_registration.binance import (
    BinanceP2PParser)
from crypto_exchanges.crypto_exchanges_registration.bybit import BybitP2PParser

BANK_NAME = os.path.basename(__file__).split('.')[0].capitalize()

TINKOFF_CURRENCIES = (
    'USD', 'EUR', 'RUB', 'GBP', 'KZT', 'BYN', 'AMD', 'TRY', 'CNY', 'JPY',
    'CHF', 'HKD'
)


class TinkoffParser(BankParser):
    bank_name: str = BANK_NAME
    endpoint: str = API_TINKOFF
    buy_and_sell: bool = True
    name_from: str = 'from'
    name_to: str = 'to'
    connection_type: str = 'Tor'
    need_cookies: bool = False

    def _create_params(self, fiats_combinations):
        params = [
            dict([(self.name_from, params[0]), (self.name_to, params[-1])])
            for params in fiats_combinations
        ]
        return params

    def _extract_buy_and_sell_from_json(self, json_data: dict
                                        ) -> tuple[float, float] or None:
        if not json_data:
            return None
        payload = json_data['payload']
        rates = payload['rates']
        buy = sell = float()
        for category in rates:
            if category['category'] == 'DepositPayments':
                buy = category.get('buy')
                sell = category.get('sell')
            if category['category'] == 'CUTransfersPremium':
                buy_premium = category.get('buy')
                sell_premium = category.get('sell')
                if buy_premium and sell_premium:
                    return buy_premium, sell_premium
        return buy, sell


class TinkoffBinanceP2PParser(BinanceP2PParser):
    bank_name: str = BANK_NAME


class TinkoffBybitP2PParser(BybitP2PParser):
    bank_name: str = BANK_NAME
