from django.urls import path

from core.views import get_all_exchanges, stop, start

app_name = 'core'

urlpatterns = [
    path('444/', get_all_exchanges, name="get_all_banks"),
    path('start/', start, name="start"),
    path('stop/', stop, name="stop"),
]
