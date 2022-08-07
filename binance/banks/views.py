from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from banks.banks_registration.tinkoff import (get_all_tinkoff,
                                              get_all_tinkoff_exchanges,
                                              get_not_looped)
from banks.banks_registration.wise import get_all_wise_exchanges
from banks.models import BanksExchangeRates


class SelectModelListView(ListView):
    def select_model(self):
        name_of_bank = self.kwargs.get('name_of_bank')
        model = BanksExchangeRates.get(name_of_bank)
        return model


class BankRatesList(ListView):
    template_name = 'banks/bank_rates.html'

    def select_model(self):
        name_of_bank = self.kwargs.get('name_of_bank')
        model = BanksExchangeRates.get(name_of_bank)
        return model

    def get_queryset(self):
        return self.select_model().objects.select_related('update').all()

    def get_context_data(self, **kwargs):
        context = super(BankRatesList, self).get_context_data(**kwargs)
        select_bank_rates = self.select_model().objects.select_related('update'
                                                                       ).all()
        context['bank_rates'] = select_bank_rates
        context['name_of_bank'] = self.kwargs.get('name_of_bank').capitalize()
        context['last_update'] = select_bank_rates.latest('update'
                                                          ).update.updated
        return context

def tinkoff_not_looped(request):
    return get_not_looped()

def tinkoff(request):
    return get_all_tinkoff_exchanges()


def tinkoff_all(request):
    return get_all_tinkoff()


def wise(request):
    return get_all_wise_exchanges()
