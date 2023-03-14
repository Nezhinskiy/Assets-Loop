
from django.shortcuts import redirect
from django.views.generic import ListView
from django_filters.views import FilterView

from core.filters import ExchangesFilter
from core.models import InfoLoop
from core.tasks import all_reg, assets_loop, assets_loop_stop
from crypto_exchanges.models import InterExchanges


def registration(request):
    all_reg.s().delay()
    if InfoLoop.objects.all().count() == 0:
        InfoLoop.objects.create(value=False)
    return redirect('core:info')


def start(request):
    if InfoLoop.objects.first().value == 0:
        InfoLoop.objects.create(value=True)
        assets_loop.s().delay()
    return redirect('core:inter_exchanges_list_new')


def stop(request):
    if InfoLoop.objects.first().value == 1:
        assets_loop_stop.s().delay()
    return redirect('core:info')


class InfoLoopList(ListView):
    model = InfoLoop
    template_name = 'crypto_exchanges/info.html'


class InterExchangesListNew(FilterView):
    """
    View displays a list of InterExchanges objects using a FilterView and a
    template called main.html. It also filters the list based on user search
    queries using a filterset called ExchangesFilter.
    """
    model = InterExchanges
    template_name = 'crypto_exchanges/main.html'
    filterset_class = ExchangesFilter
