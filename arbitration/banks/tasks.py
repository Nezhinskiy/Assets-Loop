import logging
from datetime import datetime, timezone

from arbitration.celery import app
from arbitration.settings import UPDATE_RATE
from banks.banks_registration.bank_of_georgia import BOGBinanceP2PParser
from banks.banks_registration.credo import CredoBinanceP2PParser
from banks.banks_registration.qiwi import QIWIBinanceP2PParser
from banks.banks_registration.raiffeisen import (RaiffeisenBinanceP2PParser,
                                                 RaiffeisenParser)
from banks.banks_registration.sberbank import SberbankBinanceP2PParser
from banks.banks_registration.tbc import TBCBinanceP2PParser
from banks.banks_registration.tinkoff import (TinkoffBinanceP2PParser,
                                              TinkoffParser)
from banks.banks_registration.wise import WiseBinanceP2PParser, WiseParser
from banks.banks_registration.yoomoney import YoomoneyBinanceP2PParser
from banks.currency_markets_registration.tinkoff_invest import (
    TinkoffCurrencyMarketParser)

logger = logging.getLogger(__name__)


# Banks internal rates
@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def parse_internal_tinkoff_rates(self):
    TinkoffParser().main()
    self.retry(countdown=240 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def parse_internal_raiffeisen_rates(self):
    RaiffeisenParser().main()
    self.retry(countdown=240 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def parse_internal_wise_rates(self):
    WiseParser().main()
    self.retry(countdown=240 * UPDATE_RATE[datetime.now(timezone.utc).hour])


# Banks P2P rates
@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_tinkoff_p2p_binance_exchanges(self):
    TinkoffBinanceP2PParser().main()
    self.retry(countdown=70 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_sberbank_p2p_binance_exchanges(self):
    SberbankBinanceP2PParser().main()
    self.retry(countdown=70 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_raiffeisen_p2p_binance_exchanges(self):
    RaiffeisenBinanceP2PParser().main()
    self.retry(countdown=70 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_qiwi_p2p_binance_exchanges(self):
    QIWIBinanceP2PParser().main()
    self.retry(countdown=70 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_yoomoney_p2p_binance_exchanges(self):
    YoomoneyBinanceP2PParser().main()
    self.retry(countdown=70 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_bog_p2p_binance_exchanges(self):
    BOGBinanceP2PParser().main()
    self.retry(countdown=70 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_tbc_p2p_binance_exchanges(self):
    TBCBinanceP2PParser().main()
    self.retry(countdown=70 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_credo_p2p_binance_exchanges(self):
    CredoBinanceP2PParser().main()
    self.retry(countdown=70 * UPDATE_RATE[datetime.now(timezone.utc).hour])


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_wise_p2p_binance_exchanges(self):
    WiseBinanceP2PParser().main()
    self.retry(countdown=70 * UPDATE_RATE[datetime.now(timezone.utc).hour])


# Currency markets
@app.task
def parse_currency_market_tinkoff_rates():
    TinkoffCurrencyMarketParser().main()
