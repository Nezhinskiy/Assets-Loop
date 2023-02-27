import logging

from arbitration.celery import app
from banks.banks_registration.tinkoff import TinkoffParser
from banks.banks_registration.wise import WiseParser
from banks.currency_markets_registration.tinkoff_invest import \
    TinkoffCurrencyMarketParser

from banks.banks_registration.sberbank import SberbankBinanceP2PParser
from banks.banks_registration.tinkoff import TinkoffBinanceP2PParser
from banks.banks_registration.wise import WiseBinanceP2PParser

from banks.banks_registration.raiffeisen import RaiffeisenParser, RaiffeisenBinanceP2PParser

from banks.banks_registration.qiwi import QIWIBinanceP2PParser

from banks.banks_registration.yoomoney import \
    YoomoneyBinanceP2PParser

logger = logging.getLogger(__name__)


# Banks internal rates
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
def parse_internal_raiffeisen_rates(self):
    RaiffeisenParser().main()
    self.retry(countdown=200)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def parse_internal_wise_rates(self):
    WiseParser().main()
    self.retry(countdown=200)


# Banks P2P rates
@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_tinkoff_p2p_binance_exchanges(self):
    TinkoffBinanceP2PParser().main()
    self.retry(countdown=70)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_sberbank_p2p_binance_exchanges(self):
    SberbankBinanceP2PParser().main()
    self.retry(countdown=70)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_raiffeisen_p2p_binance_exchanges(self):
    RaiffeisenBinanceP2PParser().main()
    self.retry(countdown=70)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_qiwi_p2p_binance_exchanges(self):
    QIWIBinanceP2PParser().main()
    self.retry(countdown=70)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_yoomoney_p2p_binance_exchanges(self):
    YoomoneyBinanceP2PParser().main()
    self.retry(countdown=70)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_wise_p2p_binance_exchanges(self):
    WiseBinanceP2PParser().main()
    self.retry(countdown=70)


# Currency markets
@app.task
def parse_currency_market_tinkoff_rates():
    TinkoffCurrencyMarketParser().main()
