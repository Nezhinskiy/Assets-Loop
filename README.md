# Assets-Loop - https://assetsloop.com

![example workflow](https://github.com/Nezhinskiy/Assets-Loop/actions/workflows/arbitration_workflow.yml/badge.svg)

Assets Loop is a free Open Source web application (built with Python + JavaScript) designed to assist in trading across cryptocurrency exchanges, forex markets, and banks using an arbitrage strategy. It is intended to search for all possible transaction chains and display them on the website's homepage. Currency exchange rates are continuously and concurrently parsed through a network of open and closed APIs using Tor network, proxys and direct, ensuring the rates are always up-to-date.

---

[Sponsorship](#sponsorship) | [Structure](#structure) | [Supported marketplaces](#supported-exchange-marketplaces) | [Technologies](#technologies) | [Requirements](#requirements) | [Quick start](#quick-start) | [Support](#support) | [Disclaimer](#disclaimer) | [License](#license) | [Author](#author) | [Copyright](#copyright)

## Sponsorship

This project requires financial support for its development and maintenance, primarily to cover server costs. If I could afford to pay for the server from donations, I could add many more banks, currency markets, and crypto exchanges. I'm aware that many people are parsing data from my resource, and I'm pleased that the project is helpful. However, if you could consider donating 5-10$ monthly, it would go a long way in supporting the project.

Assets Loop is not supported by any company and is developed in my spare time, and the server is paid from my personal funds.

- <a href="https://wise.com/invite/ih/mikhailn114">Wise balance</a> by my mail <b>M.Nezhinsy@yandex.ru</b>
- <a href="https://app.binance.com/qr/dplkbf425e0886624c4b98daad6cff6f4c9d">Binance balance</a> Pay ID: 366620204
- <a href="https://www.tinkoff.ru/cf/pEOtGED0cw">Tinkoff balance</a>
- <a href="https://patreon.com/nezh430">Patreon</a>
- <a href="https://boosty.to/nezh/donate">Boosty</a>

## Structure

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

## Supported Exchange marketplaces

<div>
  <h3>Supported crypto exchanges and supported deposit/withdrawal methods between crypto assets and fiat currencies:</h3>
  <div style="display:flex">
    <div style="flex:1">
      <h4><input type="checkbox" checked disabled> <a href="https://www.binance.com/ru/activity/referral-entry/CPA?fromActivityPage=true&ref=CPA_00ALEQ9QW0">Binance:</a></h4>
      <ul>
        <li><input type="checkbox" checked disabled> <a href="https://p2p.binance.com/">P2P</a></li>
        <li><input type="checkbox" checked disabled> <a href="https://www.binance.com/ru/buy-sell-crypto/">Card2CryptoExchange</a></li>
        <li><input type="checkbox" checked disabled> <a href="https://www.binance.com/ru/fiat/deposit/">Card2Wallet2CryptoExchange</a></li>
      </ul>
    </div>
    <div style="flex:1">
      <h4><input type="checkbox" checked disabled> <a href="https://www.bybit.com/">Bybit:</a></h4>
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
          <h4>Banks supporting currency conversion within the bank:</h4>
          <ul>
            <li><input type="checkbox" checked disabled> <a href="https://wise.com/invite/ih/mikhailn114/">Wise</a></li>
            <li><input type="checkbox" checked disabled> <a href="https://www.tinkoff.ru/baf/3l3TWVUF9i3/">Tinkoff</a></li>
            <li><input type="checkbox" checked disabled> <a href="https://www.raiffeisen.ru/">Raiffeisen Bank</a></li>
          </ul>
        </div>
        <div style="flex:1">
          <h4>Other supported banks:</h4>
          <ul>
            <li><input type="checkbox" checked disabled> <a href="https://bankofgeorgia.ge/">Bank of Georgia</a></li>
            <li><input type="checkbox" checked disabled> <a href="https://www.tbcbank.ge/">TBC Bank</a></li>
            <li><input type="checkbox" checked disabled> <a href="https://credobank.ge/">Credo Bank</a></li>
            <li><input type="checkbox" checked disabled> <a href="http://www.sberbank.ru/">Sberbank</a></li>
            <li><input type="checkbox" checked disabled> <a href="https://yoomoney.ru/">Yoomoney</a></li>
            <li><input type="checkbox" checked disabled> <a href="https://qiwi.com/">QIWI</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
  <div>
    <h3>Supported currency markets:</h3>
    <ul>
      <li><input type="checkbox" checked disabled> <a href="https://www.tinkoff.ru/invest/">Tinkoff Invest</a></li>
    </ul>
  </div>
</div>

## Technologies

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

## Requirements

### Up-to-date clock

The clock must be accurate, synchronized to a NTP server very frequently to avoid problems with communication to the exchanges.

### Minimum hardware required

To run this service I recommend you a cloud instance with a minimum of:

- Minimal (advised) system requirements: 2GB RAM, 1GB disk space, 2vCPU

### Software requirements

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker & Docker Compose](https://www.docker.com/products/docker)
- [Python](http://docs.python-guide.org/en/latest/starting/installation/) >= 3.9
- [pip](https://pip.pypa.io/en/stable/installing/)
- [virtualenv](https://virtualenv.pypa.io/en/stable/installation.html) (Recommended)

## Quick start

### Install Docker & Docker Compose

- Install Docker and Docker Compose on the server or local (for ubuntu):

```
sudo apt install curl                                   # installing a file download utility
curl -fsSL https://get.docker.com -o get-docker.sh      # download script for installation
sh get-docker.sh                                        # running the script
sudo apt-get install docker-compose-plugin              # install docker compose
```

### Local development

- Clone repository:
```
git clone https://github.com/Nezhinskiy/Assets-Loop.git
```

- Go to the [infra](infra) directory:
```
cd Assets-Loop/infra/
```

- Create an .env file in the [infra](infra) directory and fill it with your data as in the 
[example.env](infra/example.env) file.

- Create and run Docker containers, run command:
```
docker-compose -f local-docker-compose.yml up
```

- After a successful build, run the migrations:
```
docker compose exec arbitration python manage.py migrate
```

- Collect static:
```
docker compose exec arbitration python manage.py collectstatic --noinput
```

### Deploy to server

- Clone repository:
```
git clone https://github.com/Nezhinskiy/Assets-Loop.git
```

- Go to the [infra](infra) directory:
```
cd Assets-Loop/infra/
```

- Copy the [prod-docker-compose.yml](infra/prod-docker-compose.yml) file and the 
[nginx](infra/nginx) directory and the [certbot](infra/certbot) directory from the 
[infra](infra) directory to the server (execute commands while in the 
[infra](infra) directory):
```
scp prod-docker-compose.yml username@IP:/home/username/Assets-Loop/  # username - server username
scp -r nginx username@IP:/home/username/Assets-Loop/                 # IP - server public IP
scp -r certbot username@IP:/home/username/Assets-Loop/
```

- Go to your server, to the Assets-Loop directory:
```
ssh username@IP        # username - server username
cd Assets-Loop/        # IP - server public IP
```

- Create an .env file in the Assets-Loop directory and fill it with your data as in the 
[example.env](infra/example.env) file.

- Create and run Docker containers, run command on server:
```
docker-compose -f prod-docker-compose.yml up
```

- After a successful build, run the migrations:
```
docker compose exec arbitration python manage.py migrate
```

- Collect static:
```
docker compose exec arbitration python manage.py collectstatic --noinput
```

### Populating the database and starting the service

- In the .env file, you specified the path in the REGISTRATION_URL variable. Follow it to populate the database with the necessary data.

- In the .env file, you specified the path in the START_URL variable. Follow it to start the service.

### GitHub Actions CI

- To work with GitHub Actions, you need to create environment variables in the Secrets > Actions section of the repository:
```
DOCKER_PASSWORD         # Docker Hub password
DOCKER_USERNAME         # Docker Hub login
DOCKER_PROJECT          # Project name on Docker Hub
HOST                    # server public IP
USER                    # server username
PASSPHRASE              # *if ssh key is password protected
SSH_KEY                 # private ssh key
TELEGRAM_TO             # Telegram account ID to send a message
TELEGRAM_TOKEN          # token of the bot sending the message
```

## Support

### Help

For any questions not covered by the documentation, or for more information about the service, write to me in 
<a href="https://t.me/Mikhail_Nezhinsky">Telegram</a>.

### [Pull Requests](https://github.com/Nezhinskiy/Assets-Loop/pulls)

Feel like the service is missing a feature? I welcome your pull requests!

Please, message me on <a href="https://t.me/Mikhail_Nezhinsky">Telegram</a>, before you start working on any new feature.

## Disclaimer

This software is for educational purposes only. Do not risk money which
you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS
AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

## License

MIT license
([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

## Author

Assets Loop is owned and maintained by Mikhail Nezhinsky.

You can follow me on 
<a href="https://www.linkedin.com/in/mikhail-nezhinsky/">Linkedin</a> to keep up to date with project updates and releases. Or you can write to me on 
<a href="https://t.me/Mikhail_Nezhinsky">Telegram</a>.

## Copyright

Copyright (c) 2022-2023 Mikhail Nezhinsky