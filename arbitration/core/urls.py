from django.urls import path

from core.views import (InfoLoopList, InterExchangesAPIView,
                        InterExchangesListNew, registration, start, stop)

app_name = 'core'

urlpatterns = [
    path('', InterExchangesListNew.as_view(), name='inter_exchanges_list_new'),
    path('data/', InterExchangesAPIView.as_view(),
         name='inter_exchanges_data'),
    path('info', InfoLoopList.as_view(), name="info"),
    path('start/', start, name="start"),
    path('stop/', stop, name="stop"),
    path('reg/', registration, name="registration"),
]
