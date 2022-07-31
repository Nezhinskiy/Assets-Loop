from itertools import combinations

from banks.models import FIATS_WISE, WiseExchanges, WiseUpdates
from core.parsers import BankParser


class Wise(BankParser):
    fiats = FIATS_WISE
    endpoint = 'https://wise.com/gateway/v3/price?'
    Exchanges = WiseExchanges
    Updates = WiseUpdates
    sourceAmount = 10000
    profileCountry = 'EE'
    buy_and_sell = False

    def generate_unique_params(self) -> list[dict[str]]:
        """Repackaging a tuple with tuples into a list with params."""
        fiats = self.converts_choices_to_set(self.fiats)
        fiats_combinations = tuple(combinations(fiats, 2))  # 2: currency pair
        params_list = [dict([('sourceAmount', self.sourceAmount),
                             ('sourceCurrency', params[0]),
                             ('targetCurrency', params[-1]),
                             ('profileCountry', self.profileCountry)])
                       for params in fiats_combinations]
        return params_list

    def extract_price_from_json(self, json_data: list) -> float:

        if len(json_data) > 1:
            for exchange_data in json_data:
                if (
                        exchange_data.get('payInMethod')
                        and exchange_data.get('payOutMethod') == 'BALANCE'
                ):
                    price_before_commission = exchange_data.get('midRate')
                    commission = (exchange_data.get('variableFee')
                                  / self.sourceAmount * 100)
                    price = price_before_commission * 100 / (100 + commission)
                    return price



        # payload = json_data['payload']
        # rates = payload['rates']
        # for category in rates:
        #     if category['category'] == 'CUTransfersPremium':
        #         buy: float = category.get('buy')
        #         sell: float = category.get('sell')
        #         return buy, sell


def get_all_tinkoff():
    tinkoff_parser = Tinkoff()
    message = tinkoff_parser.get_all_api_answers()
    return message
