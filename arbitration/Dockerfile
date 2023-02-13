FROM python:3.9-slim

LABEL author='Nezhinsky'

WORKDIR /arbitration

COPY requirements.txt .

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y iputils-ping && \
    pip install --upgrade pip &&  \
    pip install --root-user-action=ignore -r requirements.txt --no-cache-dir

COPY . .

CMD gunicorn --access-logfile - --workers 3 --bind 0.0.0.0:8000 --timeout 120  arbitration.wsgi:application