import os

from core.intra_exchanges import IntraBanks, IntraBanksNotLooped
from core.parsers import BankInvestParser, BankParser

BANK_NAME = os.path.basename(__file__).split('.')[0].capitalize()

TINKOFF_CURRENCIES = (
    'RUB', 'USD', 'EUR', 'ILS', 'GBP', 'CHF', 'CAD', 'AUD', 'SGD'
)

TINKOFF_CURRENCIES_WITH_REQUISITES = ('RUB', 'USD', 'EUR', )

# FIATS_TINKOFF = (
#     ('RUB', 'Rub'),
#     ('USD', 'Usd'),
#     ('EUR', 'Eur'),
#     ('ILS', 'Ils'),
#     ('GBP', 'Gbp'),
#     ('CHF', 'Chf'),
#     ('CAD', 'Cad'),
#     ('AUD', 'Aud'),
#     ('SGD', 'Sgd'),
#     ('BGN', 'Bgn'),
#     ('BYN', 'Byn'),
#     ('AED', 'Aed'),
#     ('PLN', 'Pln'),
#     ('TRY', 'Try'),
#     ('CNY', 'Cny'),
#     ('HKD', 'Hkd'),
#     ('SEK', 'Sek'),
#     ('CZK', 'Czk'),
#     ('THB', 'Thb'),
#     ('INR', 'Inr'),
#     ('JPY', 'Jpy'),
#     ('KZT', 'Kzt'),
#     ('AMD', 'Amd'),
#     ('KRW', 'Krw'),
#     ('IDR', 'Idr'),
#     ('VND', 'Vnd'),
#     ('NOK', 'Nok')
# )


class TinkoffParser(BankParser):
    bank_name = BANK_NAME
    endpoint = 'https://api.tinkoff.ru/v1/currency_rates?'

    def create_params(self, fiats_combinations):
        params = [
            dict([(self.name_from, params[0]), (self.name_to, params[-1])])
            for params in fiats_combinations
        ]
        return params

    def extract_buy_and_sell_from_json(self, json_data: dict) -> tuple[float,
                                                                       float]:
        payload = json_data['payload']
        rates = payload['rates']
        for category in rates:
            if category['category'] == 'CUTransfersPremium':
                buy: float = category.get('buy')
                sell: float = category.get('sell')
                return buy, sell


class IntraTinkoff(IntraBanks):
    bank_name = BANK_NAME
    currencies_with_requisites = TINKOFF_CURRENCIES_WITH_REQUISITES


class IntraTinkoffNotLooped(IntraBanksNotLooped):
    bank_name = BANK_NAME


def get_tinkoff_invest_exchanges():
    tinkoff_invest_parser = BankInvestParser(BANK_NAME)
    message = tinkoff_invest_parser.main()
    return message

def get_not_looped():
    tinkoff_not_looped = IntraTinkoffNotLooped()
    message = tinkoff_not_looped.main()
    return message


def get_all_tinkoff_exchanges():
    tinkoff_parser = TinkoffParser()
    message = tinkoff_parser.main()
    return message


def get_all_tinkoff():
    get_all_tinkoff_exchanges()
    tinkoff_insider = IntraTinkoff()
    message = tinkoff_insider.main()
    return message
