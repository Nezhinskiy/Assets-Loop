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
    internal_tinkoff_rates = TinkoffParser()
    try:
        internal_tinkoff_rates.logger_start()
        internal_tinkoff_rates.main()
        internal_tinkoff_rates.logger_end()
        self.retry(countdown=200)
    except Exception as error:
        logger.error(error)
        raise Exception


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def parse_internal_wise_rates(self):
    internal_wise_rates = WiseParser()
    try:
        internal_wise_rates.logger_start()
        internal_wise_rates.main()
        internal_wise_rates.logger_end()
        self.retry(countdown=200)
    except Exception as error:
        logger.error(error)
        raise Exception


# Currency markets
@app.task
def parse_currency_market_tinkoff_rates():
    currency_market_tinkoff = TinkoffCurrencyMarketParser()
    try:
        currency_market_tinkoff.logger_start()
        currency_market_tinkoff.main()
        currency_market_tinkoff.logger_end()
    except Exception as error:
        logger.error(error)
        raise Exception
