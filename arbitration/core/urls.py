from django.urls import include, path

from core.views import (InfoLoopList, registration, start, no_tor, _tor,
                        stop)

app_name = 'core'

urlpatterns = [
    path('info', InfoLoopList.as_view(), name="info"),
    path('start/', start, name="start"),
    path('stop/', stop, name="stop"),
    path('reg/', registration, name="registration"),
    path('tor/', _tor, name="registration"),
    path('notor/', no_tor, name="registration"),
]
