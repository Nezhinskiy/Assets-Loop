from django import template

from banks.models import BankInvestExchanges, BankInvestExchangesUpdates

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
def is_empty(value):
    from banks.banks_config import BANKS_CONFIG
    currency_markets = BANKS_CONFIG[value]['bank_invest_exchanges']
    if not currency_markets:
        return True
    else:
        return False
