import logging

from arbitration.celery import app
from banks.banks_registration.tinkoff import TinkoffParser
from banks.banks_registration.wise import WiseParser
from banks.currency_markets_registration.tinkoff_invest import \
    TinkoffCurrencyMarketParser

logger = logging.getLogger(__name__)


# Banks
@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def parse_internal_tinkoff_rates(self):
    TinkoffParser().main()
    self.retry(countdown=200)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def parse_internal_wise_rates(self):
    WiseParser().main()
    self.retry(countdown=200)


# Currency markets
@app.task
def parse_currency_market_tinkoff_rates():
    TinkoffCurrencyMarketParser().main()
