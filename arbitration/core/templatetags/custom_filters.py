from datetime import datetime

from django import template

register = template.Library()


@register.filter
def last_url_path(value, num):
    print(value.split('/')[-1])
    return value.split('/')[-num - 1]


@register.filter
def is_empty(value, channel):
    from banks.banks_config import BANKS_CONFIG
    currency_markets = BANKS_CONFIG[value][channel]
    if not currency_markets:
        return True
    return False


@register.filter
def round_up(value):
    if value is None:
        return None
    target_length = 10
    length = len(str(int(value)))
    round_length = target_length - length
    return round(value, round_length)


@register.filter
def payment_channel_name(value, trade_type):
    if value == 'P2PCryptoExchangesRates':
        return 'P2P'
    if value == 'Card2Wallet2CryptoExchanges':
        if trade_type == 'BUY':
            return 'Card-Wallet-Crypto'
        return 'Crypto-Wallet-Card'
    if value == 'Card2CryptoExchanges':
        if trade_type == 'BUY':
            return 'Card-Crypto'
        return 'Crypto-Card'


@register.filter
def updated_time(value):
    seconds = int(
        (datetime.now() - value.replace(tzinfo=None)).total_seconds()
    )
    if seconds > 999:
        return 999
    return seconds
