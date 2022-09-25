from django.urls import path

from banks.views import (BankRatesList, tinkoff, tinkoff_all,
                         tinkoff_invest_exchanges, tinkoff_not_looped, wise,
                         best_bank_intra_exchanges)

app_name = 'bank_rates'

urlpatterns = [
    path('44/', tinkoff_all, name="tinkoff_all"),
    path('11/', tinkoff, name="tinkoff"),
    path('12/', wise, name="wise"),
    path('15/', tinkoff_not_looped, name="tinkoff_not_looped"),
    path('banks/<str:name_of_bank>/',
         BankRatesList.as_view(), name='name_of_bank'),
    path('55/', tinkoff_invest_exchanges, name="tinkoff_invest_exchanges"),
    path('66/', best_bank_intra_exchanges, name="best_bank_intra_exchanges")
]
