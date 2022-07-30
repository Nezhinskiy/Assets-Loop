from core.parsers import BankParser
from banks.models import FIATS_TINKOFF
from banks.models import TinkoffExchanges, TinkoffUpdates

ENDPOINT = 'https://api.tinkoff.ru/v1/currency_rates?'


class Tinkoff(BankParser):
    fiats = FIATS_TINKOFF
    endpoint = ENDPOINT
    Exchanges = TinkoffExchanges
    Updates = TinkoffUpdates

    def extract_buy_and_sell_from_json(self, json_data: dict) -> tuple[float,
                                                                       float]:
        payload = json_data['payload']
        rates = payload['rates']
        for category in rates:
            if category['category'] == 'CUTransfersPremium':
                buy: float = category.get('buy')
                sell: float = category.get('sell')
                return buy, sell


def get_all():
    tinkoff_parser = Tinkoff()
    message = tinkoff_parser.get_all_api_answers()
    return message
