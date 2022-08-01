from datetime import datetime, timedelta
from http import HTTPStatus
from sys import getsizeof

import requests
from core.parsers import P2PParser
from parses_p2p.models import (ASSETS, FIATS, PAY_TYPES, TRADE_TYPES,
                               P2PBinance, UpdateP2PBinance)


class BinanceParser(P2PParser):
    assets = ASSETS
    fiats = FIATS
    pay_types = PAY_TYPES
    trade_types = TRADE_TYPES
    endpoint = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    page = 1
    rows = 1
    Exchanges = P2PBinance
    Updates = UpdateP2PBinance

    def create_body(self, asset, trade_type, fiat, pay_types):
        return {
            "page": self.page,
            "rows": self.rows,
            "publisherType": None,
            "asset": asset,
            "tradeType": trade_type,
            "fiat": fiat,
            "payTypes": [pay_types]
        }

    def create_headers(self, body):
        return {
            "Content-Type": "application/json",
            "Content-Length": str(getsizeof(body)),
        }

    def extract_price_from_json(self, json_data: dict) -> [int | None]:
        data = json_data.get('data')
        if len(data) == 0:
            price = None
            return price
        internal_data = data[0]
        adv = internal_data.get('adv')
        price = adv.get('price')
        return price


def get_all_p2p_binance():
    binance_parser = BinanceParser()
    message = binance_parser.get_all_api_answers()
    return message
