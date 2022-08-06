from django.urls import path

from banks.views import BankRatesList, tinkoff, tinkoff_all, wise

app_name = 'bank_rates'

urlpatterns = [
    path('44/', tinkoff_all, name="tinkoff_all"),
    path('11/', tinkoff, name="tinkoff"),
    path('12/', wise, name="wise"),
    path('banks/<str:name_of_bank>/',
         BankRatesList.as_view(), name='name_of_bank'),
]
