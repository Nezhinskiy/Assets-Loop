from core.multithreading import all_exchanges

from core.models import InfoLoop


def get_all_exchanges(request):
    return all_exchanges()


def start(request):
    InfoLoop.objects.create(value=True)
    return all_exchanges()


def stop(request):
    InfoLoop.objects.create(value=False)
