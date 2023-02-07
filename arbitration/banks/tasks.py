from datetime import datetime

from dateutil import parser

from arbitration.celery import app
from banks.banks_registration.tinkoff import TinkoffParser
from banks.banks_registration.wise import WiseParser
from banks.currency_markets_registration.tinkoff_invest import \
    TinkoffCurrencyMarketParser
from core.models import InfoLoop


# Banks time
@app.task
def bank_start_time():
    print('banks_start')
    return datetime.now()


# Banks
@app.task
def parse_internal_tinkoff_rates():
    tinkoff_parser = TinkoffParser()
    print('tinkoff_rates')
    tinkoff_parser.main()


@app.task
def parse_internal_wise_rates():
    wise_parser = WiseParser()
    print('wise_rates')
    wise_parser.main()


# Currency markets
@app.task
def parse_currency_market_tinkoff_rates():
    tinkoff_currency_market_parser = TinkoffCurrencyMarketParser()
    print('tinkoff_currency_market_rates')
    tinkoff_currency_market_parser.main()


# Best bank rates
@app.task
def best_bank_intra_exchanges(str_start_time):
    start_time = parser.parse(str_start_time[0])
    print('!!!!!!!!!!!!!!!!!!!!!1___', start_time)
    print('banks_end')
    duration = datetime.now() - start_time
    new_loop = InfoLoop.objects.filter(value=True).last()
    new_loop.all_banks_exchanges = duration
    new_loop.save()
