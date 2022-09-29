from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from threading import Thread
from multiprocessing import Process
from datetime import datetime

from banks.banks_registration.tinkoff import (get_all_tinkoff,
                                              get_all_tinkoff_exchanges,
                                              get_tinkoff_not_looped,
                                              get_tinkoff_invest_exchanges)
from banks.banks_registration.wise import get_all_wise_exchanges, get_wise_not_looped
from banks.models import BanksExchangeRates, Banks
from core.intra_exchanges import BestBankIntraExchanges

from banks.multithreading import all_banks_exchanges
from banks.banks_config import BANKS_CONFIG


def banks(request):
    template = 'banks/banks.html'
    return render(request, template)


class BanksRatesList(ListView):
    template_name = 'banks/bank_rates.html'

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(BanksRatesList, self).get_context_data(**kwargs)
        context['banks_name'] = list(BANKS_CONFIG.keys())
        context['bank_rates'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class BankRatesList(ListView):
    template_name = 'banks/bank_rates.html'

    def get_bank_name(self):
        return self.kwargs.get('bank_name').capitalize()

    def get_queryset(self):
        bank = Banks.objects.get(name=self.get_bank_name())
        return self.model.objects.filter(bank=bank)

    def get_context_data(self, **kwargs):
        context = super(BankRatesList, self).get_context_data(**kwargs)
        context['banks_name'] = list(BANKS_CONFIG.keys())
        context['bank_rates'] = self.get_queryset()
        context['bank_name'] = self.get_bank_name()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class BankIntraExchanges(BankRatesList):
    model = BanksExchangeRates


class BanksIntraExchanges(BanksRatesList):
    model = BanksExchangeRates


def tinkoff_not_looped(request):
    return get_tinkoff_not_looped()


def wise_not_looped(request):
    return get_wise_not_looped()


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
