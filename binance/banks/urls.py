from django.urls import path

from banks.views import (BankIntraExchanges, best_bank_intra_exchanges, tinkoff,
                         tinkoff_all, tinkoff_invest_exchanges,
                         tinkoff_not_looped, wise, wise_not_looped,
                         get_all_banks_exchanges, banks, BanksIntraExchanges)

app_name = 'banks'

urlpatterns = [
    path('44/', tinkoff_all, name="tinkoff_all"),
    path('11/', tinkoff, name="tinkoff"),
    path('12/', wise, name="wise"),
    path('15/', tinkoff_not_looped, name="tinkoff_not_looped"),
    path('banks/', banks, name='banks'),
    path('banks/intra_exchanges/',
         BanksIntraExchanges.as_view(), name='banks_intra_exchanges'),
    path('<str:bank_name>/intra_exchanges/',
         BankIntraExchanges.as_view(), name='bank_intra_exchanges'),
    path('55/', tinkoff_invest_exchanges, name="tinkoff_invest_exchanges"),
    path('66/', best_bank_intra_exchanges, name="best_bank_intra_exchanges"),
    path('16/', wise_not_looped, name="wise_not_looped"),
    path('116/', get_all_banks_exchanges, name="all_banks_exchanges"),
]
