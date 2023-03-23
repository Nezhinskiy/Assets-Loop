# Assets-Loop - Arbitration Web Application Project

![example workflow](https://github.com/Nezhinskiy/Assets-Loop/actions/workflows/arbitration_workflow.yml/badge.svg)

https://assetsloop.com

## Description:
Assets Loop is a free open-source web application (built with Python + JavaScript) designed to assist in trading across cryptocurrency exchanges, forex markets, and banks using an arbitrage strategy. It is intended to search for all possible transaction chains and display them on the website's homepage. Currency exchange rates are continuously and concurrently parsed through a network of open and closed APIs using Tor network, proxys and direct, ensuring the rates are always up-to-date.
### Supported Crypto Exchanges:
- [X] [Binance](https://www.binance.com/)
- [X] [Bybit](https://www.bybit.com/)

#### Binance-supported input/output methods between crypto assets and fiat currencies:
- [X] [P2P](https://p2p.binance.com/)
- [X] [Card2CryptoExchange](https://www.binance.com/ru/buy-sell-crypto/)
- [X] [Card2Wallet2CryptoExchange](https://www.binance.com/ru/fiat/deposit/)

#### Bybit-supported input/output methods between crypto assets and fiat currencies:
- [X] [P2P](https://www.bybit.com/fiat/trade/otc/)

### Supported Banks:
- [X] [Wise](https://wise.com/)
- [X] [Bank of Georgia](https://bankofgeorgia.ge/)
- [X] [TBC Bank](https://www.tbcbank.ge/)
- [X] [Credo Bank](https://credobank.ge/)
- [X] [Tinkoff](https://www.tinkoff.ru/)
- [X] [Sberbank](http://www.sberbank.ru/)
- [X] [Raiffeisen Bank](https://www.raiffeisen.ru/)
- [X] [Yoomoney](https://yoomoney.ru/)
- [X] [QIWI](https://qiwi.com/)

#### Banks supporting currency conversion within the bank:
- [X] [Wise](https://wise.com/)
- [X] [Tinkoff](https://www.tinkoff.ru/)
- [X] [Raiffeisen Bank](https://www.raiffeisen.ru/)

### Supported currency exchanges:
- [X] [Tinkoff Invest](https://www.tinkoff.ru/invest/)

## Technologies:
This is a web application project using Docker Compose for containerization. The project includes several services such as a Tor proxy to bypass parsing locks, Redis, PostgreSQL database, Nginx web server, Certbot for SSL certification, and Celery workflows for parsing, parsing and computing data. These services are connected to the user's network.

- Python 3
- Django, Django REST framework
- Celery, Celery Beat, 
- Redis
- Docker, Docker-Compose
- PostgreSQL
- NGINX, Certbot, Gunicorn
- JavaScript, jQuery
- DataTables, Ajax
- Bootstrap, Select2, Twix
- CI/CD, Git Actions
- Digital Ocean

## Disclaimer
This software is for educational purposes only. Do not risk money which
you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS
AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

## License
- MIT license
  ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

## Copyright
Copyright (c) 2022-2023 Mikhail Nezhinsky