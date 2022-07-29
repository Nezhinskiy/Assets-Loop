from binance.banks.BankParser import BankParser

from binance.banks.models import FIATS

ENDPOINT = 'https://api.tinkoff.ru/v1/currency_rates?'


class Tinkoff(BankParser):
    fiats = FIATS
    endpoint = ENDPOINT
    model = None

    def extract_buy_and_sell_from_json(self, json_data: dict) -> list[float]:
        payload = json_data['payload']
        rates = payload['rates']
        for category in rates:
            if category['category'] == 'CUTransfersPremium':
                buy: float = category.get('buy')
                sell: float = category.get('sell')
                return [buy, sell]


tinkoff_parser = Tinkoff()
message = tinkoff_parser.get_all_api_answers()
print(message)
