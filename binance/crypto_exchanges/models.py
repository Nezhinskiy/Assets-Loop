from django.db import models

from banks.models import Banks
from core.models import UpdatesModel


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
    bank = models.ForeignKey(
        Banks, related_name='p2p_rates', on_delete=models.CASCADE
    )
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(
        P2PCryptoExchangesRatesUpdates, related_name='datas',
        on_delete=models.CASCADE
    )


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


class Card2Wallet2CryptoExchangesUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_wallet_2_crypto_exchanges_update',
        on_delete=models.CASCADE
    )


class Card2Wallet2CryptoExchanges(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='card_2_wallet_2_crypto_exchanges',
        on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=4)
    fiat = models.CharField(max_length=3)
    trade_type = models.CharField(max_length=4)
    transaction_method = models.CharField(max_length=35)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(Card2Wallet2CryptoExchangesUpdates,
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
    pre_price = models.FloatField(null=True, blank=True, default=None)
    commission = models.FloatField(null=True, blank=True, default=None)
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


class BestPaymentChannelsUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='best_payment_channel_update',
        on_delete=models.CASCADE
    )


class BestPaymentChannels(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='best_payment_channel',
        on_delete=models.CASCADE
    )
    bank = models.ForeignKey(
        Banks, related_name='best_payment_channel',
        on_delete=models.CASCADE
    )
    asset = models.CharField(max_length=4)
    fiat = models.CharField(max_length=3)
    trade_type = models.CharField(max_length=4)
    price = models.FloatField(null=True, blank=True, default=None)
    payment_channel_model = models.CharField(max_length=30)
    exchange_id = models.PositiveSmallIntegerField()
    update = models.ForeignKey(
        BestPaymentChannelsUpdates, related_name='datas',
        on_delete=models.CASCADE
    )


class BestCombinationPaymentChannelsUpdates(UpdatesModel):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges,
        related_name='best_combinations_payment_channels_update',
        on_delete=models.CASCADE
    )


class BestCombinationPaymentChannels(models.Model):
    crypto_exchange = models.ForeignKey(
        CryptoExchanges, related_name='best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    input_bank = models.ForeignKey(
        Banks, related_name='input_bank_best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    output_bank = models.ForeignKey(
        Banks, related_name='output_bank_best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    input_exchange = models.ForeignKey(
        BestPaymentChannels,
        related_name='input_exchange_best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    interim_exchange = models.ForeignKey(
        IntraCryptoExchanges,
        related_name='interim_exchange_best_combinations_payment_channels',
        blank=True, null=True, on_delete=models.CASCADE
    )
    output_exchange = models.ForeignKey(
        BestPaymentChannels,
        related_name='output_exchange_best_combinations_payment_channels',
        on_delete=models.CASCADE
    )
    from_fiat = models.CharField(max_length=3)
    to_fiat = models.CharField(max_length=3)
    price = models.FloatField(null=True, blank=True, default=None)
    update = models.ForeignKey(
        BestCombinationPaymentChannelsUpdates, related_name='datas',
        on_delete=models.CASCADE
    )
