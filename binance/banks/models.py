from django.db import models

from core.models import BankExchangesModel, ExchangeUpdatesModel

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
        TinkoffUpdates, related_name='datas', on_delete=models.CASCADE
    )
