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
@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def parse_internal_tinkoff_rates(self):
    internal_tinkoff_rates = TinkoffParser()
    internal_tinkoff_rates.logger_start()
    internal_tinkoff_rates.main()
    internal_tinkoff_rates.logger_end()
    self.retry(countdown=200)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def parse_internal_wise_rates(self):
    internal_wise_rates = WiseParser()
    internal_wise_rates.logger_start()
    internal_wise_rates.main()
    internal_wise_rates.logger_end()
    self.retry(countdown=200)


# Currency markets
@app.task
def parse_currency_market_tinkoff_rates():
    currency_market_tinkoff = TinkoffCurrencyMarketParser()
    currency_market_tinkoff.logger_start()
    currency_market_tinkoff.main()
    currency_market_tinkoff.logger_end()


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
