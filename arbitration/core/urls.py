from django.urls import path

from core.views import get_all_exchanges, start, stop, InfoLoopList, registration

app_name = 'core'

urlpatterns = [
    path('', InfoLoopList.as_view(), name="home"),
    path('444/', get_all_exchanges, name="get_all_banks"),
    path('start/', start, name="start"),
    path('stop/', stop, name="stop"),
    path('reg/', registration, name="registration"),
]
