import os

from core.parsers import BankInvestParser, BankParser

BANK_NAME = os.path.basename(__file__).split('.')[0].capitalize()

TINKOFF_CURRENCIES = (
    'USD', 'EUR', 'RUB', 'ILS', 'GBP', 'CHF', 'CAD', 'AUD', 'SGD', 'HKD',
    'TRY', 'KZT', 'BYN', 'AMD'
)

TINKOFF_CURRENCIES_WITH_REQUISITES = ('RUB', 'USD', 'EUR', )


class TinkoffParser(BankParser):
    bank_name = BANK_NAME
    endpoint = 'https://api.tinkoff.ru/v1/currency_rates?'
    buy_and_sell = True
    name_from = 'from'
    name_to = 'to'

    def create_params(self, fiats_combinations):
        params = [
            dict([(self.name_from, params[0]), (self.name_to, params[-1])])
            for params in fiats_combinations
        ]
        return params

    def extract_buy_and_sell_from_json(self, json_data: dict
                                       ) -> tuple[float, float] or None:
        if not json_data:
            return
        payload = json_data['payload']
        rates = payload['rates']
        buy = sell = float()
        for category in rates:
            if category['category'] == 'DepositPayments':
                buy: float = category.get('buy')
                sell: float = category.get('sell')
            if category['category'] == 'CUTransfersPremium':
                buy_premium: float = category.get('buy')
                sell_premium: float = category.get('sell')
                if buy_premium and sell_premium:
                    return buy_premium, sell_premium
        return buy, sell


def get_all_tinkoff_exchanges():
    tinkoff_parser = TinkoffParser()
    message = tinkoff_parser.main()
    return message
