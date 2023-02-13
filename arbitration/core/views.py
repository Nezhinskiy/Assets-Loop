import time

from celery import chain, chord, group
from django.shortcuts import redirect
from django.views.generic import ListView

from banks.tasks import (best_bank_intra_exchanges,
                         parse_currency_market_tinkoff_rates,
                         parse_internal_tinkoff_rates,
                         parse_internal_wise_rates)
from core.models import InfoLoop
from core.registration import all_registration
from core.tasks import (assets_loop, end_all_exchanges, end_banks_exchanges,
                        end_crypto_exchanges,
                        get_complex_binance_tinkoff_inter_exchanges_calculate,
                        get_complex_binance_wise_inter_exchanges_calculate,
                        get_simpl_binance_tinkoff_inter_exchanges_calculate,
                        get_simpl_binance_wise_inter_exchanges_calculate, tor, notor, all_reg)
from crypto_exchanges.tasks import (best_crypto_exchanges_intra_exchanges,
                                    crypto_exchanges_start_time,
                                    get_all_binance_crypto_exchanges,
                                    get_all_card_2_wallet_2_crypto_exchanges,
                                    get_binance_card_2_crypto_exchanges,
                                    get_tinkoff_p2p_binance_exchanges,
                                    get_wise_p2p_binance_exchanges)


class InfoLoopList(ListView):
    model = InfoLoop
    template_name = 'crypto_exchanges/info.html'

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(InfoLoopList, self).get_context_data(**kwargs)
        context['info_loops'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest('updated').updated
        context['loops_count'] = self.get_queryset().filter(value=1).count
        return context


def start(request):
    if InfoLoop.objects.last().value == 0:
        assets_loop.s().delay()
    return redirect('crypto_exchanges:InterExchangesListNew')


def stop(request):
    if InfoLoop.objects.last().value == 1:
        InfoLoop.objects.create(value=False)
    return redirect('crypto_exchanges:InterExchangesListNew')


def registration(request):
    all_reg.s().delay()
    return redirect('core:info')

def no_tor(request):
    notor.s().delay()
    return redirect('core:info')
def _tor(request):
    tor.s().delay()
    return redirect('core:info')
