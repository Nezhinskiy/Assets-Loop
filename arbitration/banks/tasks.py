import logging

from arbitration.celery import app
from banks.banks_registration.tinkoff import TinkoffParser
from banks.banks_registration.wise import WiseParser
from banks.currency_markets_registration.tinkoff_invest import \
    TinkoffCurrencyMarketParser

from banks.banks_registration.sberbank import \
    SberbankBinanceP2PParser, SimplBinanceSberbankInterExchangesCalculating
from banks.banks_registration.tinkoff import \
    TinkoffBinanceP2PParser, SimplBinanceTinkoffInterExchangesCalculating, \
    ComplexBinanceTinkoffInterExchangesCalculating
from banks.banks_registration.wise import WiseBinanceP2PParser, \
    SimplBinanceWiseInterExchangesCalculating, \
    ComplexBinanceWiseInterExchangesCalculating

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
def get_wise_p2p_binance_exchanges(self):
    WiseBinanceP2PParser().main()
    self.retry(countdown=70)


@app.task(
    bind=True, max_retries=None, queue='parsing', autoretry_for=(Exception,),
    retry_backoff=True
)
def get_sberbank_p2p_binance_exchanges(self):
    SberbankBinanceP2PParser().main()
    self.retry(countdown=70)


# Currency markets
@app.task
def parse_currency_market_tinkoff_rates():
    TinkoffCurrencyMarketParser().main()


# Inter exchanges calculating
@app.task
def get_simpl_binance_tinkoff_inter_exchanges_calculating():
    SimplBinanceTinkoffInterExchangesCalculating().main()


@app.task
def get_complex_binance_tinkoff_inter_exchanges_calculating():
    ComplexBinanceTinkoffInterExchangesCalculating().main()


@app.task
def get_simpl_binance_wise_inter_exchanges_calculating():
    SimplBinanceWiseInterExchangesCalculating().main()


@app.task
def get_complex_binance_wise_inter_exchanges_calculating():
    ComplexBinanceWiseInterExchangesCalculating().main()


@app.task
def get_simpl_binance_sberbank_inter_exchanges_calculating():
    SimplBinanceSberbankInterExchangesCalculating().main()
