# Assets Loop - Arbitration Web Application Project

![example workflow](https://github.com/Nezhinskiy/binance_api/actions/workflows/arbitration_workflow.yml/badge.svg)

[![github actions ci badge]][github actions ci]
[license-mit-badge]: https://img.shields.io/badge/License-MIT%202.0-blue.svg?style=flat-square

[Go to site](https://assetsloop.com/)

## Description:
Assets Loop - is a free web application to help you trade between cryptocurrencies and fiat currencies. Corrected by source code written in Python + JavaScript. It is designed to search for all possible chains of transactions between banks, currency exchanges and crypto-exchanges and display them on the main page of the site ranked by margin percentage. Parsing of exchange rates for a variety of open and closed APIs is carried out continuously and multi-threaded through the Tor network, which guarantees the constant relevance of exchange rates.

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
- DataTables
- Bootstrap
- Continuous Integration, Continuous Deployment
- Digital Ocean

## License
- MIT license
  ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

## Copyright
Copyright (c) 2022-2023 Mikhail Nezhinsky