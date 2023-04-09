# Assets-Loop - https://assetsloop.com

![example workflow](https://github.com/Nezhinskiy/Assets-Loop/actions/workflows/arbitration_workflow.yml/badge.svg)

## Structure:
<pre>
.
├── <a href=".github/workflows">.github/workflows</a> ─ Workflow for Git Actions CI
├── <a href="arbitration">arbitration</a> ─ Django project
│   ├── <a href="arbitration/arbitration">arbitration</a> ─ Django settings module
│   ├── <a href="arbitration/banks">banks</a> ─ Banks & Currency Markets creation module
│   ├── <a href="arbitration/core">core</a> ─ View module
│   ├── <a href="arbitration/crypto_exchanges">crypto_exchanges</a> ─ Crypto Exchanges creation module
│   ├── <a href="arbitration/parsers">parsers</a> ─ <b>Business logic module</b>
│   ├── <a href="arbitration/static">static</a> ─ css, javascript, favicon
│   └── <a href="arbitration/templates">templates</a> ─ HTML pages
└── <a href="infra">infra</a> ─ Project infrastructure setup
</pre>

## Description:
Assets Loop is a free Open Source web application (built with Python + JavaScript) designed to assist in trading across cryptocurrency exchanges, forex markets, and banks using an arbitrage strategy. It is intended to search for all possible transaction chains and display them on the website's homepage. Currency exchange rates are continuously and concurrently parsed through a network of open and closed APIs using Tor network, proxys and direct, ensuring the rates are always up-to-date.
<div>
  <h3>Supported Crypto Exchanges:</h3>
  <ul>
    <li><input type="checkbox" checked disabled> <a href="https://www.binance.com/">Binance</a></li>
    <li><input type="checkbox" checked disabled> <a href="https://www.bybit.com/">Bybit</a></li>
  </ul>
  <h4>Crypto Exchanges supported input/output methods between crypto assets and fiat currencies:</h4>
  <div style="display:flex">
    <div style="flex:1">
      <h4>Binance:</h4>
      <ul>
        <li><input type="checkbox" checked disabled> <a href="https://p2p.binance.com/">P2P</a></li>
        <li><input type="checkbox" checked disabled> <a href="https://www.binance.com/ru/buy-sell-crypto/">Card2CryptoExchange</a></li>
        <li><input type="checkbox" checked disabled> <a href="https://www.binance.com/ru/fiat/deposit/">Card2Wallet2CryptoExchange</a></li>
      </ul>
    </div>
    <div style="flex:1">
      <h4>Bybit:</h4>
      <ul>
        <li><input type="checkbox" checked disabled> <a href="https://www.bybit.com/fiat/trade/otc/">P2P</a></li>
        <li><input type="checkbox" disabled> <a href="https://www.bybit.com/fiat/trade/express/home/">Card2CryptoExchange</a></li>
        <li><input type="checkbox" disabled> <a href="https://www.bybit.com/fiat/trade/deposit/home/">Card2Wallet2CryptoExchange</a></li>
      </ul>
    </div>
  </div>

  <div style="display:flex">
    <div style="flex:1">
      <h3>Supported Banks:</h3>
      <div style="display:flex">
        <div style="flex:1">
          <h4>Added support for currency conversion within the bank:</h4>
          <li><input type="checkbox" checked disabled> <a href="https://wise.com/">Wise</a></li>
          <li><input type="checkbox" checked disabled> <a href="https://www.tinkoff.ru/">Tinkoff</a></li>
          <li><input type="checkbox" checked disabled> <a href="https://www.raiffeisen.ru/">Raiffeisen Bank</a></li>
        </div>
        <div style="flex:1">
          <h4>Support for currency conversion within the bank has not been added:</h4>
          <li><input type="checkbox" checked disabled> <a href="https://bankofgeorgia.ge/">Bank of Georgia</a></li>
          <li><input type="checkbox" checked disabled> <a href="https://www.tbcbank.ge/">TBC Bank</a></li>
          <li><input type="checkbox" checked disabled> <a href="https://credobank.ge/">Credo Bank</a></li>
          <li><input type="checkbox" checked disabled> <a href="http://www.sberbank.ru/">Sberbank</a></li>
          <li><input type="checkbox" checked disabled> <a href="https://yoomoney.ru/">Yoomoney</a></li>
          <li><input type="checkbox" checked disabled> <a href="https://qiwi.com/">QIWI</a></li>
        </div>
      </div>
    </div>
    <div style="flex:1">
      <h3>Supported currency exchanges:</h3>
      <ul>
        <li><input type="checkbox" checked disabled> <a href="https://www.tinkoff.ru/invest/">Tinkoff Invest</a></li>
      </ul>
    </div>
  </div>
</div>

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