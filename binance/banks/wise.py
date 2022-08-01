from banks.models import FIATS_WISE, WiseExchanges, WiseUpdates
from core.parsers import BankParser


class Wise(BankParser):
    fiats = FIATS_WISE
    endpoint = 'https://wise.com/gateway/v3/price?'
    Exchanges = WiseExchanges
    Updates = WiseUpdates
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


def get_all_wise():
    wise_parser = Wise()
    message = wise_parser.get_all_api_answers()
    return message
