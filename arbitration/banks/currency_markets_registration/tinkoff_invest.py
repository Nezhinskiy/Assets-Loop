import os
from datetime import datetime, time

import pytz
from _decimal import Decimal

from arbitration.settings import API_TINKOFF_INVEST
from core.parsers import BankInvestParser

CURRENCY_MARKET_NAME = (
    os.path.basename(__file__).split('.')[0].capitalize().replace('_', ' '))


class TinkoffCurrencyMarketParser(BankInvestParser):
    currency_markets_name = CURRENCY_MARKET_NAME
    endpoint = API_TINKOFF_INVEST
    link_ends = ('USDRUB', 'EURRUB')
    # 'GBPRUB', 'HKDRUB', 'TRYRUB', 'KZTRUB_TOM', 'BYNRUB_TOM', 'AMDRUB_TOM',
    # 'CHFRUB', 'JPYRUB',
    connection_type: str = 'Direct'
    need_cookies: bool = False
    waiting_time: str = 5
    LIMIT_TRY: int = 6

    @staticmethod
    def _get_utc_work_time() -> bool:
        start_work_time = time(hour=7)
        end_work_time = time(hour=19)
        time_zone = 'Europe/Moscow'
        local_datatime = datetime.now(pytz.timezone(time_zone))
        if_work_day = local_datatime.weekday() in range(0, 5)
        if_work_time = start_work_time <= local_datatime.time() < end_work_time
        return if_work_day and if_work_time

    @staticmethod
    def _extract_buy_and_sell_from_json(json_data: dict, link_end: str
                                        ) -> tuple[Decimal, Decimal]:
        items = json_data['payload']['items']
        for item in items:
            content = item['content']
            instruments = content['instruments']
            for instrument in instruments:
                if not instrument:
                    continue
                ticker = instrument.get('ticker')
                if ticker == link_end:
                    relative_yield = Decimal(instrument['relativeYield'])
                    pre_price = Decimal(instrument['price'])
                    price = pre_price + pre_price / 100 * relative_yield
                    if link_end[0:3] == 'KZT':
                        price /= 100
                    elif link_end[0:3] == 'AMD':
                        price /= 100
                    buy_price = price - price * Decimal('0.003')
                    sell_price = (1 / price) - (1 / price) * Decimal('0.003')
                    return buy_price, sell_price
