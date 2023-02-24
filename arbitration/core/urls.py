from django.urls import include, path

from core.views import (InfoLoopList, registration, start,
                        stop, InfoCoreList)

app_name = 'core'

urlpatterns = [
    path('info', InfoLoopList.as_view(), name="info"),
    path('info-core', InfoCoreList.as_view(), name="info_core"),
    path('start/', start, name="start"),
    path('stop/', stop, name="stop"),
    path('reg/', registration, name="registration"),
]
