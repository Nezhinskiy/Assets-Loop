from bank_rates.models import FIATS_TINKOFF, TinkoffExchanges, TinkoffUpdates
from core.parsers import BankParser

from calculations.inside_banks import InsideBanks

from calculations.models import InsideTinkoffExchanges, InsideTinkoffUpdates

TINKOFF_CURRENCIES_WITH_REQUISITES = ('RUB', 'USD', 'EUR', )


class TinkoffParser(BankParser):
    fiats = FIATS_TINKOFF
    endpoint = 'https://api.tinkoff.ru/v1/currency_rates?'
    Exchanges = TinkoffExchanges
    Updates = TinkoffUpdates

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


class InsideTinkoff(InsideBanks):
    fiats = FIATS_TINKOFF
    Exchanges = TinkoffExchanges
    InsideExchanges = InsideTinkoffExchanges
    Updates = InsideTinkoffUpdates
    currencies_with_requisites = TINKOFF_CURRENCIES_WITH_REQUISITES


def get_all_tinkoff_exchanges():
    tinkoff_parser = TinkoffParser()
    message = tinkoff_parser.main()
    return message


def get_all_tinkoff():
    get_all_tinkoff_exchanges()
    tinkoff_insider = InsideTinkoff()
    message = tinkoff_insider.main()
    return message
