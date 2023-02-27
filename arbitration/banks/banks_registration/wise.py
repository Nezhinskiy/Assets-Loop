import os

from core.parsers import BankParser

from crypto_exchanges.crypto_exchanges_registration.binance import \
    BinanceP2PParser

BANK_NAME = os.path.basename(__file__).split('.')[0].capitalize()

WISE_CURRENCIES = (
    'USD', 'EUR', 'ILS', 'GBP', 'CHF', 'CAD', 'AUD', 'SGD', 'GEL'
)

WISE_CURRENCIES_WITH_REQUISITES = ('USD', 'EUR', )


class WiseParser(BankParser):
    bank_name: str = BANK_NAME
    endpoint: str = 'https://wise.com/gateway/v3/price?'
    name_from: str = 'sourceCurrency'
    name_to: str = 'targetCurrency'
    buy_and_sell: bool = False
    # custom_settings
    sourceAmount: int = 10000
    profileCountry: str = 'RU'

    def create_params(self, fiats_combinations):
        params = [dict([('sourceAmount', self.sourceAmount),
                        ('sourceCurrency', params[0]),
                        ('targetCurrency', params[-1]),
                        ('profileCountry', self.profileCountry)])
                  for params in fiats_combinations]
        return params

    def extract_price_from_json(self, json_data: list) -> float:
        if json_data and len(json_data) > 1:
            for exchange_data in json_data:
                if (
                        exchange_data.get('payInMethod') ==
                        exchange_data.get('payOutMethod') == 'BALANCE'
                ):
                    price_before_commission = exchange_data.get('midRate')
                    commission = (exchange_data.get('total')
                                  / self.sourceAmount * 100)
                    price = price_before_commission * 100 / (100 + commission)
                    return price


class WiseBinanceP2PParser(BinanceP2PParser):
    bank_name: str = BANK_NAME
