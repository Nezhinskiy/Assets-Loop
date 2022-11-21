from rest_framework import serializers

from crypto_exchanges.models import InterExchanges, CryptoExchanges, P2PCryptoExchangesRates, IntraCryptoExchanges, InterExchangesUpdates

from banks.models import Banks, BanksExchangeRates, CurrencyMarkets


class RoundingDecimalField(serializers.DecimalField):
    def validate_precision(self, value):
        return value


class CryptoExchangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoExchanges
        fields = ('name',)


class BanksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banks
        fields = ('name',)


class IntraCryptoExchangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntraCryptoExchanges
        exclude = ['id', 'update', 'crypto_exchange']


class P2PCryptoExchangesRatesSerializer(serializers.ModelSerializer):
    intra_crypto_exchange = IntraCryptoExchangesSerializer(read_only=True)

    class Meta:
        model = P2PCryptoExchangesRates
        exclude = ['id', 'update']


class CurrencyMarketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyMarkets
        fields = ('name',)


class BanksExchangeRatesSerializer(serializers.ModelSerializer):
    bank = BanksSerializer(read_only=True)
    currency_market = CurrencyMarketsSerializer(read_only=True)

    class Meta:
        model = BanksExchangeRates
        exclude = ['id', 'update']


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterExchangesUpdates
        fields = ('updated',)


class InterExchangesSerializer(serializers.ModelSerializer):
    crypto_exchange = CryptoExchangesSerializer(read_only=True)
    input_bank = BanksSerializer(read_only=True)
    output_bank = BanksSerializer(read_only=True)
    input_crypto_exchange = P2PCryptoExchangesRatesSerializer(read_only=True)
    output_crypto_exchange = P2PCryptoExchangesRatesSerializer(read_only=True)
    interim_crypto_exchange = IntraCryptoExchangesSerializer(read_only=True)
    second_interim_crypto_exchange = IntraCryptoExchangesSerializer(
        read_only=True)
    bank_exchange = BanksExchangeRatesSerializer(read_only=True)
    marginality_percentage = RoundingDecimalField(max_digits=4, decimal_places=2)
    update = UpdateSerializer(read_only=True)

    class Meta:
        model = InterExchanges
        exclude = ['id']
