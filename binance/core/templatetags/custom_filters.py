from django import template

from banks.models import BankInvestExchanges, BankInvestExchangesUpdates
from core.intra_exchanges import get_related_exchange

register = template.Library()


@register.filter
def last_url_path(value, num):
    return value.split('/')[-num - 1]


@register.filter
def get_currency_markets_rates(value):
    from banks.banks_config import BANKS_CONFIG
    currency_markets_name = BANKS_CONFIG[value]['bank_invest_exchanges']
    return BankInvestExchanges.objects.filter(
        currency_market__name__in=currency_markets_name
    )


@register.filter
def count_rates(value):
    from banks.banks_config import BANKS_CONFIG
    name = last_url_path(value, 2)
    if name != 'banks':
        currency_markets_name = BANKS_CONFIG[name]['bank_invest_exchanges']
        return BankInvestExchanges.objects.filter(
            currency_market__name__in=currency_markets_name
        ).count()
    else:
        return BankInvestExchanges.objects.all().count()


@register.filter
def last_update(value):
    from banks.banks_config import BANKS_CONFIG
    name = last_url_path(value, 2)
    if name != 'banks':
        currency_markets_name = BANKS_CONFIG[name]['bank_invest_exchanges']
        return BankInvestExchangesUpdates.objects.filter(
            currency_market__name__in=currency_markets_name
        ).last().updated
    else:
        return BankInvestExchangesUpdates.objects.all().last().updated


@register.filter
def is_empty(value, channel):
    from banks.banks_config import BANKS_CONFIG
    currency_markets = BANKS_CONFIG[value][channel]
    if not currency_markets:
        return True
    else:
        return False


@register.filter
def is_not_card_2_crypto(value):
    from banks.banks_config import BANKS_CONFIG
    from crypto_exchanges.models import Card2CryptoExchanges
    payment_channels = BANKS_CONFIG[value]['payment_channels']
    if Card2CryptoExchanges not in payment_channels:
        return True
    else:
        return False


register.filter('get_related_exchange', get_related_exchange)


@register.filter
def round_up(value):
    target_length = 10
    length = len(str(int(value)))
    round_length = target_length - length
    return round(value, round_length)
