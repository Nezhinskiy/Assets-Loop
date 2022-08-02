from banks.models import FIATS_TINKOFF, TinkoffExchanges, TinkoffUpdates
from core.parsers import BankParser


class Tinkoff(BankParser):
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


def get_all_tinkoff_exchanges():
    tinkoff_parser = Tinkoff()
    message = tinkoff_parser.main()
    return message
