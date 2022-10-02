from crypto_exchanges.crypto_exchanges_registration.binance import (
    get_all, get_all_binance_crypto_exchanges,
    get_all_card_2_wallet_2_crypto_exchanges, get_all_p2p_binance_exchanges,
    get_best_card_2_card_crypto_exchanges, get_best_crypto_exchanges,
    get_binance_card_2_crypto_exchanges, get_binance_fiat_crypto_list,
    get_inter_exchanges_calculate)
from django.views.generic import ListView

from banks.banks_config import BANKS_CONFIG

from banks.models import Banks

from crypto_exchanges.models import CryptoExchanges, P2PCryptoExchangesRates


class CryptoExchangesInternalExchanges(ListView):
    model = P2PCryptoExchangesRates
    template_name = 'crypto_exchanges/crypto_exchange_internal_exchanges.html'


class CryptoExchangeInternalExchanges(ListView):
    model = P2PCryptoExchangesRates
    template_name = 'crypto_exchanges/crypto_exchange_internal_exchanges.html'


class CryptoExchangesRatesList(ListView):
    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import (
            CRYPTO_EXCHANGES_CONFIG)
        context = super(CryptoExchangesRatesList,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class CryptoExchangeRatesList(ListView):
    def get_crypto_exchange_name(self):
        return self.kwargs.get('crypto_exchange_name').capitalize()

    def get_bank_name(self):
        return self.kwargs.get('bank_name').capitalize()

    def get_queryset(self):
        if self.get_crypto_exchange_name() != 'Crypto_exchanges':
            crypto_exchange = CryptoExchanges.objects.get(
                name=self.get_crypto_exchange_name())
            if self.get_bank_name() != 'Banks':
                bank = Banks.objects.get(name=self.get_bank_name())
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange, bank=bank)
            else:
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange)
        else:
            bank = Banks.objects.get(name=self.get_bank_name())
            return self.model.objects.filter(bank=bank)

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import (
            CRYPTO_EXCHANGES_CONFIG)
        context = super(CryptoExchangeRatesList,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['crypto_exchange_name'] = self.get_crypto_exchange_name()
        context['bank_name'] = self.get_bank_name()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class CryptoExchangesP2PExchanges(CryptoExchangesRatesList):
    model = P2PCryptoExchangesRates
    template_name = 'crypto_exchanges/crypto_exchange_p2p_exchanges.html'


class CryptoExchangeP2PExchanges(CryptoExchangeRatesList):
    model = P2PCryptoExchangesRates
    template_name = 'crypto_exchanges/crypto_exchange_p2p_exchanges.html'


def p2p_binance(request):
    return get_all_p2p_binance_exchanges()


def binance_crypto(request):
    return get_all_binance_crypto_exchanges()


def card_2_wallet_2_crypto(request):
    return get_all_card_2_wallet_2_crypto_exchanges()


def binance_fiat_crypto_list(request):
    return get_binance_fiat_crypto_list()


def binance_card_2_crypto_exchanges(request):
    return get_binance_card_2_crypto_exchanges()


def binance_best_crypto_exchanges(request):
    return get_best_crypto_exchanges()


def binance_best_card_2_card_crypto_exchanges(request):
    return get_best_card_2_card_crypto_exchanges()


def binance_inter_exchanges_calculate(request):
    return get_inter_exchanges_calculate()


def all(request):
    return get_all()
