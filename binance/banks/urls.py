from banks.views import tinkoff, wise, BankRatesList
from django.urls import path

app_name = 'banks'

urlpatterns = [
    path('11/', tinkoff, name="tinkoff"),
    path('12/', wise, name="wise"),
    path('banks/<str:name_of_bank>/',
         BankRatesList.as_view(), name='name_of_bank'),
]
