from django.urls import path

from banks.views import (BankBestExchange, BankInternalExchange,
                         BankInternalTripleExchange, BankInvestExchange,
                         BanksBestExchange, BanksInternalExchange,
                         BanksInternalTripleExchange, BanksInvestExchange,
                         banks, best_bank_intra_exchanges,
                         get_all_banks_exchanges, tinkoff, tinkoff_all,
                         tinkoff_invest_exchanges, tinkoff_not_looped, wise,
                         wise_not_looped)

app_name = 'banks'

urlpatterns = [
    path('banks/internal_exchanges/',
         BanksInternalExchange.as_view(), name='banks_internal_exchanges'),
    path('<str:bank_name>/internal_exchanges/',
         BankInternalExchange.as_view(), name='bank_internal_exchanges'),
    path('banks/internal_triple_exchanges/',
         BanksInternalTripleExchange.as_view(),
         name='banks_internal_triple_exchanges'),
    path('<str:bank_name>/internal_triple_exchanges/',
         BankInternalTripleExchange.as_view(),
         name='bank_internal_triple_exchanges_exchanges'),
    path('banks/currency_markets/',
         BanksInvestExchange.as_view(), name='banks_currency_market_exchanges'),
    path('<str:bank_name>/currency_markets/',
         BankInvestExchange.as_view(), name='bank_currency_market_exchanges'),
    path('banks/best_exchanges/',
         BanksBestExchange.as_view(), name='banks_best_exchanges'),
    path('<str:bank_name>/best_exchanges/',
         BankBestExchange.as_view(), name='bank_best_exchanges'),
    path('44/', tinkoff_all, name="tinkoff_all"),
    path('11/', tinkoff, name="tinkoff"),
    path('12/', wise, name="wise"),
    path('15/', tinkoff_not_looped, name="tinkoff_not_looped"),
    path('banks/', banks, name='banks'),
    path('55/', tinkoff_invest_exchanges, name="tinkoff_invest_exchanges"),
    path('66/', best_bank_intra_exchanges, name="best_bank_intra_exchanges"),
    path('16/', wise_not_looped, name="wise_not_looped"),
    path('116/', get_all_banks_exchanges, name="all_banks_exchanges"),
]
