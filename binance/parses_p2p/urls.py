from django.urls import include, path
from rest_framework import routers

from parses_p2p.views import index

app_name = 'parses_p2p'

urlpatterns = [
    path('', index, name="index"),
]
