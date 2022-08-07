from django.urls import path

from banks.views import BankRatesList, tinkoff, tinkoff_all, wise, tinkoff_not_looped

app_name = 'bank_rates'

urlpatterns = [
    path('44/', tinkoff_all, name="tinkoff_all"),
    path('11/', tinkoff, name="tinkoff"),
    path('12/', wise, name="wise"),
    path('15/', tinkoff_not_looped, name="tinkoff_not_looped"),
    path('banks/<str:name_of_bank>/',
         BankRatesList.as_view(), name='name_of_bank'),
]
