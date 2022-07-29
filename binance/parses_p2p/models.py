from django.db import models

from binance.models import ExchangeUpdatesModel, P2PExchangesModel

ASSETS = (
    ('USDT', 'USDT'),
    ('BUSD', 'BUSD'),
    ('BTC', 'BTC'),
    ('ETH', 'ETH'),
)
TRADE_TYPES = (
    ('BUY', 'buy'),
    ('SELL', 'sell')
)
FIATS = (
    ('RUB', 'rub'),
    ('USD', 'usd'),
    ('EUR', 'eur'),
    ('GBP', 'gbp'),
)
PAY_TYPES = (
    ('Tinkoff', 'Tinkoff'),
    ('Wise', 'Wise'),
    # 'TBCbank',
    # 'BankofGeorgia',
    ('RosBank', 'RosBank'),
    # ('RUBfiatbalance', 'RUBfiatbalance')
)


class UpdateP2PBinance(ExchangeUpdatesModel):
    pass


class P2PBinance(P2PExchangesModel):
    ASSETS = ASSETS
    TRADE_TYPES = TRADE_TYPES
    FIATS = FIATS
    PAY_TYPES = PAY_TYPES
    update = models.ForeignKey(
         UpdateP2PBinance, related_name='datas', on_delete=models.CASCADE
    )

    def __str__(self):
        return self.price
