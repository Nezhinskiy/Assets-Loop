from django.urls import path

from arbitration.settings import (INFO_URL, REGISTRATION_URL, START_URL,
                                  STOP_URL)
from core.views import (InfoLoopList, InterExchangesAPIView,
                        InterExchangesListNew, registration, start, stop)

app_name = 'core'

urlpatterns = [
    path('', InterExchangesListNew.as_view(), name='inter_exchanges_list_new'),
    path('data/', InterExchangesAPIView.as_view(),
         name='inter_exchanges_data'),
    path(INFO_URL, InfoLoopList.as_view(), name="info"),
    path(START_URL, start, name="start"),
    path(STOP_URL, stop, name="stop"),
    path(REGISTRATION_URL, registration, name="registration"),
]
