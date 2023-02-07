from django.urls import path

from banks.views import (BankInternalExchange, BanksInternalExchange, banks,
                         get_all_banks_exchanges, tinkoff,
                         tinkoff_invest_exchanges, wise)

app_name = 'banks'

urlpatterns = [
    path('banks/internal_exchanges/',
         BanksInternalExchange.as_view(), name='banks_internal_exchanges'),
    path('<str:bank_name>/internal_exchanges/',
         BankInternalExchange.as_view(), name='bank_internal_exchanges'),
    path('11/', tinkoff, name="tinkoff"),
    path('12/', wise, name="wise"),
    path('banks/', banks, name='banks'),
    path('55/', tinkoff_invest_exchanges, name="tinkoff_invest_exchanges"),
    path('116/', get_all_banks_exchanges, name="all_banks_exchanges"),
]
