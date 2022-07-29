from binance.models import ExchangeUpdatesModel, BankExchangesModel
from django.db import models


FIATS_TINKOFF = (
    ('RUB', 'Rub'),
    ('USD', 'Usd'),
    ('EUR', 'Eur'),
    ('ILS', 'Ils'),
)


class TinkoffUpdates(ExchangeUpdatesModel):
    pass


class TinkoffExchanges(BankExchangesModel):
    FIATS = FIATS_TINKOFF
    update = models.ForeignKey(
        TinkoffUpdates, related_name='%(class)s', on_delete=models.CASCADE
    )