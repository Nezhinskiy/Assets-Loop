from rest_framework import serializers

from banks.models import Banks, BanksExchangeRates, CurrencyMarkets
from crypto_exchanges.models import (CryptoExchanges, CryptoExchangesRates,
                                     InterExchanges, InterExchangesUpdates,
                                     IntraCryptoExchangesRates)

ROUND_TO = 10


class RoundingDecimalField(serializers.DecimalField):
    """
    Custom redefinition of the display of decimal numbers.
    """
    MIN_NON_EMPTY_DECIMAL: int = 5

    def __init__(self, max_digits, decimal_places, percent=False, **kwargs):
        super().__init__(max_digits, decimal_places, **kwargs)
        self.percent = percent

    def validate_precision(self, value):
        return value

    def quantize(self, value):
        """
        Quantize the decimal value to the configured precision.
        """
        if self.percent:
            return round(value, self.decimal_places)
        integers, real_decimal_places = map(
            len, str(value).split('.'))
        max_decimal_places = self.max_digits - integers
        if real_decimal_places > max_decimal_places:
            self.decimal_places = max_decimal_places
        if integers >= self.max_digits:
            self.decimal_places = 1
        result = round(value, self.decimal_places)
        if result == int(result):
            return round(value, 1)
        return result


class CryptoExchangesSerializer(serializers.ModelSerializer):
    """
    A serializer for the CryptoExchanges model, which represents a
    cryptocurrency exchange.
    """
    class Meta:
        model = CryptoExchanges
        fields = ('name',)


class BanksSerializer(serializers.ModelSerializer):
    """
    A serializer for the Banks model, which represents a bank.
    """
    class Meta:
        model = Banks
        fields = ('name',)


class IntraCryptoExchangesRatesSerializer(serializers.ModelSerializer):
    """
    A serializer for the IntraCryptoExchangesRates model, which represents
    exchange rates between two cryptocurrencies on a single exchange.
    """
    price = RoundingDecimalField(max_digits=ROUND_TO, decimal_places=None)

    class Meta:
        model = IntraCryptoExchangesRates
        exclude = ('id', 'update', 'crypto_exchange')


class CryptoExchangesRatesSerializer(serializers.ModelSerializer):
    """
    A serializer for the CryptoExchangesRates model, which represents exchange
    rates between a cryptocurrency on a single exchange and a fiat currency on
    banks.
    """
    intra_crypto_exchange = IntraCryptoExchangesRatesSerializer(read_only=True)
    price = RoundingDecimalField(max_digits=ROUND_TO, decimal_places=None)

    class Meta:
        model = CryptoExchangesRates
        exclude = (
            'id', 'update', 'trade_type', 'crypto_exchange', 'bank'
        )


class CurrencyMarketsSerializer(serializers.ModelSerializer):
    """
    A serializer for the CurrencyMarkets model, which represents a market for
    exchanging currencies.
    """
    class Meta:
        model = CurrencyMarkets
        fields = ('name',)


class BanksExchangeRatesSerializer(serializers.ModelSerializer):
    """
    A serializer for the BanksExchangeRates model, which represents exchange
    rates between two fiat currencies at a bank.
    """
    bank = BanksSerializer(read_only=True)
    currency_market = CurrencyMarketsSerializer(read_only=True)
    price = RoundingDecimalField(max_digits=ROUND_TO, decimal_places=None)

    class Meta:
        model = BanksExchangeRates
        exclude = ('id', 'update')


class UpdateSerializer(serializers.ModelSerializer):
    """
    A serializer for the InterExchangesUpdates model, which represents
    updates to the exchange rates between two fiat currencies on a bank or
    between a cryptocurrency and a fiat currency on an exchange.
    """
    class Meta:
        model = InterExchangesUpdates
        fields = ('updated',)


class InterExchangesSerializer(serializers.ModelSerializer):
    """
    A serializer for the InterExchanges model, which represents an exchange of
    currency or cryptocurrency between two banks and between a bank and an
    exchange.
    """
    crypto_exchange = CryptoExchangesSerializer(read_only=True)
    input_bank = BanksSerializer(read_only=True)
    output_bank = BanksSerializer(read_only=True)
    input_crypto_exchange = CryptoExchangesRatesSerializer(read_only=True)
    output_crypto_exchange = CryptoExchangesRatesSerializer(read_only=True)
    interim_crypto_exchange = IntraCryptoExchangesRatesSerializer(
        read_only=True)
    second_interim_crypto_exchange = IntraCryptoExchangesRatesSerializer(
        read_only=True)
    bank_exchange = BanksExchangeRatesSerializer(read_only=True)
    marginality_percentage = RoundingDecimalField(
        max_digits=4, decimal_places=2, percent=True
    )
    update = UpdateSerializer(read_only=True)

    class Meta:
        model = InterExchanges
        fields = '__all__'
