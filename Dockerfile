FROM python:3.7.4

RUN apt-get update && \
    apt-get install -y \
        apt-transport-https \
        netcat

COPY requirements.txt /requirements.txt
RUN pip3.7 install -r requirements.txt

RUN mkdir -p /var/log/app

ENV PYTHONPATH "${PYTHONPATH}:/tickers/"

COPY common /tickers/common
COPY fill_database /tickers/fill_database
COPY web /tickers/web

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY tickers.txt /tickers.txt

ENTRYPOINT ["/entrypoint.sh"]
