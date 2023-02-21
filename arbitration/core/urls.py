from django.urls import include, path

from core.views import (InfoLoopList, registration, start, no_tor, _tor,
                        stop, c2cs, c2cb, InfoCoreList)

app_name = 'core'

urlpatterns = [
    path('info', InfoLoopList.as_view(), name="info"),
    path('info-core', InfoCoreList.as_view(), name="info_core"),
    path('start/', start, name="start"),
    path('stop/', stop, name="stop"),
    path('reg/', registration, name="registration"),
    path('tor/', _tor, name="registration"),
    path('notor/', no_tor, name="registration"),
    path('c2cs/', c2cs, name="registration"),
    path('c2cb/', c2cb, name="registration"),
]
