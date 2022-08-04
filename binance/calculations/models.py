from core.models import InsideBanksExchangesModel, ExchangeUpdatesModel
from django.db import models
from bank_rates.models import FIATS_WISE, FIATS_TINKOFF


class InsideTinkoffUpdates(ExchangeUpdatesModel):
    pass


class InsideTinkoffExchanges(InsideBanksExchangesModel):
    FIATS = FIATS_TINKOFF

    update = models.ForeignKey(
        InsideTinkoffUpdates, related_name='datas', on_delete=models.CASCADE
    )


class InsideWiseUpdates(ExchangeUpdatesModel):
    pass


class InsideWiseExchanges(InsideBanksExchangesModel):
    FIATS = FIATS_WISE

    update = models.ForeignKey(
        InsideWiseUpdates, related_name='datas', on_delete=models.CASCADE
    )
