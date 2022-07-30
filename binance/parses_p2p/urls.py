from django.urls import include, path
from parses_p2p.views import index
from rest_framework import routers

app_name = 'parses_p2p'

urlpatterns = [
    path('', index, name="index"),
]
