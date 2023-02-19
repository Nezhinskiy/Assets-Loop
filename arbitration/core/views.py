import time

from django.shortcuts import redirect
from django.views.generic import ListView

from core.models import InfoLoop
from core.tasks import (assets_loop, end_all_exchanges, end_banks_exchanges,
                        end_crypto_exchanges,
                        get_complex_binance_tinkoff_inter_exchanges_calculate,
                        get_complex_binance_wise_inter_exchanges_calculate,
                        get_simpl_binance_tinkoff_inter_exchanges_calculate,
                        get_simpl_binance_wise_inter_exchanges_calculate, tor, notor, all_reg, c2c_s, c2c_b)


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
    if InfoLoop.objects.first().value == 0:
        assets_loop.s().delay()
        time.sleep(0.1)
    return redirect('crypto_exchanges:InterExchangesListNew')


def stop(request):
    if InfoLoop.objects.first().value == 1:
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


def c2cs(request):
    c2c_s.s().delay()
    return redirect('core:info')


def c2cb(request):
    c2c_b.s().delay()
    return redirect('core:info')
