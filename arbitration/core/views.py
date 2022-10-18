from django.shortcuts import redirect
from django.views.generic import ListView

from core.models import InfoLoop
from core.multithreading import all_exchanges
from core.registration import all_registration


class InfoLoopList(ListView):
    model = InfoLoop
    template_name = 'core/home.html'

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super(InfoLoopList, self).get_context_data(**kwargs)
        context['info_loops'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest(
            'updated').updated
        context['loops_count'] = self.get_queryset().filter(value=1).count
        return context


def get_all_exchanges(request):
    return all_exchanges()


def start(request):
    try:
        if InfoLoop.objects.last().value == 0:
            InfoLoop.objects.create(value=True)
            all_exchanges()
    except AttributeError:
        InfoLoop.objects.create(value=True)
        all_exchanges()
    return redirect('core:home')


def stop(request):
    if InfoLoop.objects.last().value == 1:
        InfoLoop.objects.create(value=False)
    return redirect('core:home')


def registration(request):
    all_registration()
    return redirect('core:home')