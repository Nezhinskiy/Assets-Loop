from core.models import ExchangeUpdatesModel, P2PExchangesModel, BankExchangesModel
from django.db import models


ASSETS = (
    ('ETH', 'ETH'),
    ('BTC', 'BTC'),
    ('BUSD', 'BUSD'),
    ('USDT', 'USDT'),
)
TRADE_TYPES = (
    ('BUY', 'buy'),
    ('SELL', 'sell')
)
FIATS = (
    ('RUB', 'rub'),
    # ('USD', 'usd'),
    # ('EUR', 'eur'),
    # ('GBP', 'gbp'),
)
PAY_TYPES = (
    ('Tinkoff', 'Tinkoff'),
    ('Wise', 'Wise'),
    # 'TBCbank',
    # 'BankofGeorgia',
    ('RosBank', 'RosBank'),
    ('RUBfiatbalance', 'RUBfiatbalance')
)


class BinanceUpdates(ExchangeUpdatesModel):
    pass


class BinanceExchanges(P2PExchangesModel):
    ASSETS = ASSETS
    TRADE_TYPES = TRADE_TYPES
    FIATS = FIATS
    PAY_TYPES = PAY_TYPES
    update = models.ForeignKey(
         BinanceUpdates, related_name='datas', on_delete=models.CASCADE
    )


class BinanceCryptoUpdates(ExchangeUpdatesModel):
    pass


class BinanceCryptoExchanges(BankExchangesModel):
    FIATS = ASSETS

    update = models.ForeignKey(
        BinanceCryptoUpdates, related_name='datas', on_delete=models.CASCADE
    )
