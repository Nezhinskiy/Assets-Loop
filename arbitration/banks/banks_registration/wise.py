import os

from core.intra_exchanges import IntraBanks
from core.parsers import BankParser

BANK_NAME = os.path.basename(__file__).split('.')[0].capitalize()

WISE_CURRENCIES = (
    'USD', 'EUR', 'ILS', 'GBP', 'CHF', 'CAD', 'AUD', 'SGD', 'GEL'
)

WISE_CURRENCIES_WITH_REQUISITES = ('USD', 'EUR', )

FIATS_WISE = (
    ('USD', 'Usd'),
    ('EUR', 'Eur'),
    ('ILS', 'Ils'),
    ('GBP', 'Gbp'),
    ('CHF', 'Chf'),
    ('CAD', 'Cad'),
    ('AUD', 'Aud'),
    ('SGD', 'Sgd'),
    ('BGN', 'Bgn'),
    ('BYN', 'Byn'),
    ('AED', 'Aed'),
    ('PLN', 'Pln'),
    ('TRY', 'Try'),
    ('CNY', 'Cny'),
    ('HKD', 'Hkd'),
    ('SEK', 'Sek'),
    ('CZK', 'Czk'),
    ('THB', 'Thb'),
    ('INR', 'Inr'),
    ('JPY', 'Jpy'),
    ('KZT', 'Kzt'),
    ('AMD', 'Amd'),
    ('KRW', 'Krw'),
    ('IDR', 'Idr'),
    ('VND', 'Vnd'),
    ('NOK', 'Nok'),
)


class WiseParser(BankParser):
    bank_name = BANK_NAME
    fiats = FIATS_WISE
    endpoint = 'https://wise.com/gateway/v3/price?'
    name_from = 'sourceCurrency'
    name_to = 'targetCurrency'
    buy_and_sell = False
    # custom_settings
    sourceAmount = 10000
    profileCountry = 'RU'

    def create_params(self, fiats_combinations):
        params = [dict([('sourceAmount', self.sourceAmount),
                        ('sourceCurrency', params[0]),
                        ('targetCurrency', params[-1]),
                        ('profileCountry', self.profileCountry)])
                  for params in fiats_combinations]
        return params

    def extract_price_from_json(self, json_data: list) -> float:
        if len(json_data) > 1:
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


class IntraWise(IntraBanks):
    bank_name = BANK_NAME
    fiats = FIATS_WISE
    currencies_with_requisites = WISE_CURRENCIES_WITH_REQUISITES


def get_all_wise_exchanges():
    wise_parser = WiseParser()
    message = wise_parser.main()
    return message


def get_all_wise():
    get_all_wise_exchanges()
    wise_insider = IntraWise()
    message = wise_insider.main()
    return message
