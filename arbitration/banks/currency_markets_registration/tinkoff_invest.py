import os
from datetime import datetime, time

import pytz

from core.parsers import BankInvestParser

CURRENCY_MARKET_NAME = (
    os.path.basename(__file__).split('.')[0].capitalize().replace('_', ' '))


class TinkoffCurrencyMarketParser(BankInvestParser):
    currency_markets_name = CURRENCY_MARKET_NAME
    endpoint = ('https://www.tinkoff.ru/api/invest-gw/'
                'social/post/feed/v1/post/instrument/')
    link_ends = (
        'USDRUB', 'EURRUB'
    )
    # 'GBPRUB', 'HKDRUB', 'TRYRUB', 'KZTRUB_TOM', 'BYNRUB_TOM', 'AMDRUB_TOM',
    # 'CHFRUB', 'JPYRUB',

    @staticmethod
    def get_utc_work_time() -> bool:
        start_work_time = time(hour=7)
        end_work_time = time(hour=19)
        time_zone = 'Europe/Moscow'
        local_datatime = datetime.now(pytz.timezone(time_zone))
        if_work_day = local_datatime.weekday() in range(0, 5)
        if_work_time = start_work_time <= local_datatime.time() < end_work_time
        return if_work_day and if_work_time

    def get_api_answer(self, link_end: str) -> dict:
        """Делает запрос к эндпоинту API Tinfoff."""
        endpoint = self.endpoint + link_end
        return self.get_api_answer_get(endpoint=endpoint)

    @staticmethod
    def extract_buy_and_sell_from_json(json_data: dict, link_end: str
                                       ) -> tuple:
        items = json_data['payload']['items']
        for item in items:
            content = item['content']
            instruments = content['instruments']
            for instrument in instruments:
                if not instrument:
                    continue
                ticker = instrument.get('ticker')
                if ticker == link_end:
                    relative_yield = instrument['relativeYield']
                    pre_price = instrument['price']
                    price = pre_price + pre_price / 100 * relative_yield
                    if link_end[0:3] == 'KZT':
                        price /= 100
                    elif link_end[0:3] == 'AMD':
                        price /= 100
                    buy_price = price - price * 0.003
                    sell_price = (1 / price) - (1 / price) * 0.003
                    return buy_price, sell_price

    def calculates_buy_and_sell_data(self, link_end: str,
                                     answer: dict) -> tuple[dict, dict]:
        buy_price, sell_price = self.extract_buy_and_sell_from_json(answer,
                                                                    link_end)
        buy_data = {
            'from_fiat': link_end[0:3],
            'to_fiat': link_end[3:6],
            'price': buy_price
        }
        sell_data = {
            'from_fiat': link_end[3:6],
            'to_fiat': link_end[0:3],
            'price': sell_price
        }
        return buy_data, sell_data

    def get_all_api_answers(self) -> None:
        for link_end in self.link_ends:
            answer = self.get_api_answer(link_end)
            if answer is False:
                continue
            buy_and_sell_data = self.calculates_buy_and_sell_data(link_end,
                                                                  answer)
            for buy_or_sell_data in buy_and_sell_data:
                self.add_to_bulk_update_or_create(
                    buy_or_sell_data
                )
