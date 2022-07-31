from django.db import models

from core.models import BankExchangesModel, ExchangeUpdatesModel

FIATS_TINKOFF = (
    ('RUB', 'Rub'),
    ('USD', 'Usd'),
    ('EUR', 'Eur'),
    ('ILS', 'Ils'),
)
FIATS_WISE = (
    ('USD', 'Usd'),
    ('EUR', 'Eur'),
    ('ILS', 'Ils'),
    ('PLN', 'Pln'),
)


class TinkoffUpdates(ExchangeUpdatesModel):
    pass


class TinkoffExchanges(BankExchangesModel):
    FIATS = FIATS_TINKOFF
    update = models.ForeignKey(
        TinkoffUpdates, related_name='datas', on_delete=models.CASCADE
    )


class WiseUpdates(ExchangeUpdatesModel):
    pass


class WiseExchanges(BankExchangesModel):
    FIATS = FIATS_WISE
    update = models.ForeignKey(
        WiseUpdates, related_name='datas', on_delete=models.CASCADE
    )
