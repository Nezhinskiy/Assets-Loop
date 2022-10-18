from datetime import datetime
from multiprocessing import Process
from threading import Thread

from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.views.generic import ListView

from banks.banks_config import BANKS_CONFIG
from banks.banks_registration.tinkoff import (get_all_tinkoff,
                                              get_all_tinkoff_exchanges)
from banks.banks_registration.wise import get_all_wise_exchanges
from banks.currency_markets_registration.tinkoff_invest import \
    get_tinkoff_invest_exchanges
from banks.models import (BankInvestExchanges, Banks, BanksExchangeRates,
                          BestBankExchanges)
from banks.multithreading import all_banks_exchanges
from core.django_shortcuts.shurtcuts import get_queryset_or_404
from core.intra_exchanges import BestBankIntraExchanges


def banks(request):
    template = 'banks/banks.html'
    return render(request, template)


class BanksRatesList(ListView):

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(BanksRatesList, self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['bank_rates'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class BankRatesList(ListView):

    def get_bank_name(self):
        return self.kwargs.get('bank_name').capitalize()

    def get_queryset(self):
        bank = Banks.objects.get(name=self.get_bank_name())
        return self.model.objects.filter(bank=bank)

    def get_context_data(self, **kwargs):
        context = super(BankRatesList, self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['bank_rates'] = self.get_queryset()
        context['bank_name'] = self.get_bank_name()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class BankInternalExchange(BankRatesList):
    model = BanksExchangeRates
    template_name = 'banks/internal_exchange.html'


class BanksInternalExchange(BanksRatesList):
    model = BanksExchangeRates
    template_name = 'banks/internal_exchange.html'


class BankInvestExchange(BankRatesList):
    template_name = 'banks/currency_market_exchanges.html'
    model = BankInvestExchanges

    def get_queryset(self):
        currency_markets_name = (
            BANKS_CONFIG[self.get_bank_name()]['bank_invest_exchanges']
        )
        return get_queryset_or_404(
            self.model, currency_market__name__in=currency_markets_name
        )


class BanksInvestExchange(BanksRatesList):
    template_name = 'banks/currency_market_exchanges.html'
    model = BankInvestExchanges


class BankBestExchange(BankRatesList):
    model = BestBankExchanges
    template_name = 'banks/best_exchange.html'


class BanksBestExchange(BanksRatesList):
    model = BestBankExchanges
    template_name = 'banks/best_exchange.html'


def tinkoff(request):
    return get_all_tinkoff_exchanges()


def tinkoff_all(request):
    return get_all_tinkoff()


def tinkoff_invest_exchanges(request):
    return get_tinkoff_invest_exchanges()


def wise(request):
    return get_all_wise_exchanges()


def best_bank_intra_exchanges(request):
    get_best_bank_intra_exchanges = BestBankIntraExchanges()
    return get_best_bank_intra_exchanges.main()


def get_all_banks_exchanges(request):
    all_banks_exchanges()
