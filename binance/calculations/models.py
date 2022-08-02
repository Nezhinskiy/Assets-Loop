from core.models import InsideBanksExchangesModel, ExchangeUpdatesModel
from django.db import models
from banks.models import FIATS_WISE


class InsideWiseUpdates(ExchangeUpdatesModel):
    pass


class InsideWiseExchanges(InsideBanksExchangesModel):
    FIATS = FIATS_WISE

    update = models.ForeignKey(
        InsideWiseUpdates, related_name='datas', on_delete=models.CASCADE
    )
