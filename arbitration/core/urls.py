from django.urls import path

from core.views import (InfoLoopList, get_all_exchanges, registration, start,
                        stop)

app_name = 'core'

urlpatterns = [
    path('info', InfoLoopList.as_view(), name="info"),
    path('444/', get_all_exchanges, name="get_all_banks"),
    path('start/', start, name="start"),
    path('stop/', stop, name="stop"),
    path('reg/', registration, name="registration"),
]
