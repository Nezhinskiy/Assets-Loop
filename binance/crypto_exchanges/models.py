from django.db import models

from core.models import UpdatesModel
from banks.models import Banks


class CryptoExchanges(models.Model):
    name = models.CharField(max_length=10, null=True, blank=True)


class P2PCryptoExchangesRatesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='p2p_rates_update',
        on_delete=models.CASCADE
    )


class P2PCryptoExchangesRates(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='p2p_rates', on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=4)
    fiat = models.CharField(max_length=3)
    trade_type = models.CharField(max_length=4)
    pay_type = models.CharField(max_length=16)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(P2PCryptoExchangesRatesUpdates,
                               related_name='datas', on_delete=models.CASCADE)


class IntraCryptoExchangesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='crypto_exchanges_update',
        on_delete=models.CASCADE
    )


class IntraCryptoExchanges(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='crypto_exchanges',
        on_delete=models.CASCADE
    )
    from_asset = models.CharField(max_length=4)
    to_asset = models.CharField(max_length=4)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(
        IntraCryptoExchangesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )


class Card2Fiat2CryptoExchangesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_fiat_2_crypto_exchanges_update',
        on_delete=models.CASCADE
    )


class Card2Fiat2CryptoExchanges(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_fiat_2_crypto_exchanges',
        on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=4)
    fiat = models.CharField(max_length=3)
    trade_type = models.CharField(max_length=4)
    transaction_method = models.CharField(max_length=35)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(Card2Fiat2CryptoExchangesUpdates,
                               related_name='datas', on_delete=models.CASCADE)


class Card2CryptoExchangesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_crypto_exchanges_update',
        on_delete=models.CASCADE
    )


class Card2CryptoExchanges(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_crypto_exchanges',
        on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=4)
    fiat = models.CharField(max_length=3)
    trade_type = models.CharField(max_length=4)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(Card2CryptoExchangesUpdates,
                               related_name='datas', on_delete=models.CASCADE)


class ListsFiatCryptoUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='list_fiat_crypto_update',
        on_delete=models.CASCADE
    )


class ListsFiatCrypto(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='list_fiat_crypto',
        on_delete=models.CASCADE
    )
    list_fiat_crypto = models.JSONField()
    trade_type = models.CharField(max_length=4)
    update = models.ForeignKey(
        ListsFiatCryptoUpdates, related_name='datas', on_delete=models.CASCADE
    )
