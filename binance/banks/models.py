from django.db import models

from core.models import UpdatesModel


class Banks(models.Model):
    name = models.CharField(max_length=10, null=True, blank=True)


class BanksExchangeRatesUpdates(UpdatesModel):
    bank = models.ForeignKey(
        Banks, related_name='bank_rates_update', on_delete=models.CASCADE
    )


class BanksExchangeRates(models.Model):
    bank = models.ForeignKey(
        Banks, related_name='bank_rates', on_delete=models.CASCADE
    )
    from_fiat = models.CharField(max_length=3)
    to_fiat = models.CharField(max_length=3)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(
        BanksExchangeRatesUpdates, related_name='datas', on_delete=models.CASCADE
    )


class IntraBanksExchangesUpdates(UpdatesModel):
    bank = models.ForeignKey(
        Banks, related_name='bank_exchanges_update', on_delete=models.CASCADE
    )


class IntraBanksExchanges(models.Model):
    bank = models.ForeignKey(
        Banks, related_name='bank_exchanges', on_delete=models.CASCADE
    )
    list_of_transfers = models.JSONField()
    marginality_percentage = models.FloatField(
        null=True, blank=True, default=None
    )
    update = models.ForeignKey(
        IntraBanksExchangesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )
