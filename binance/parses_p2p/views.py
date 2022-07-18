from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from parses_p2p.parse import p2p_binance_bulk_update_or_create


def index(request):
    return p2p_binance_bulk_update_or_create()
