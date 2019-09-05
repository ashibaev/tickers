FROM nginx:1.17.2-alpine

RUN mkdir /var/log/nginx/tickers

RUN rm /etc/nginx/conf.d/default.conf
COPY default.conf /etc/nginx/conf.d
