from functools import wraps

import flask
from flask import make_response, render_template, url_for
from playhouse.shortcuts import model_to_dict

from app.app import app
from models import Ticker, Share, RelationType, TransactionType, OwnerType, InsiderTrade, Insider
from utils import InsiderData

__all__ = []


def format_response(template_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            api_request = flask.request.path.startswith('/api')
            if api_request:
                return response
            data = response.json
            return make_response(render_template(template_name, **data))

        return wrapper

    return decorator


@app.route('/favicon.ico/')
def icon():
    return flask.redirect(url_for('static', filename='favicon.ico'))


@app.route('/api/')
@app.route('/')
@format_response('tickers.html')
def tickers() -> flask.Response:
    ticker_names = list(x.name for x in Ticker.select(Ticker.name))
    response = {
        'tickers': [
            {
                'ticker_name': ticker_name,
                'href': flask.request.base_url + ticker_name + '/'
            }
            for ticker_name in ticker_names
        ]
    }
    return flask.jsonify(response)


@app.route('/api/<string:ticker_name>/')
@app.route('/<string:ticker_name>/')
@format_response('shares.html')
def shares(ticker_name: str) -> flask.Response:
    ticker = Ticker.get(Ticker.name == ticker_name)
    share_models = (
        Share.select()
            .where(Share.ticker == ticker)
    )
    response = {
        'ticker_name': ticker_name,
        'insiders_href': flask.request.base_url + 'insider/',
        'shares': list(map(model_to_dict, share_models))
    }
    return flask.jsonify(response)


def select_insider_trades():
    return (
        InsiderTrade.select(InsiderTrade, RelationType, OwnerType, TransactionType, Insider)
            .join_from(InsiderTrade, RelationType)
            .join_from(InsiderTrade, OwnerType)
            .join_from(InsiderTrade, TransactionType)
            .join_from(InsiderTrade, Insider)
    )


def patch_insider_hrefs(trades, base_url):
    for trade in trades:
        insider_name = trade['insider']['name']
        insider_nasdaq_id = trade['insider']['nasdaq_id']
        insider_str = str(InsiderData(insider_name, insider_nasdaq_id))
        trade['insider']['href'] = base_url + insider_str
    return trades


@app.route('/api/<string:ticker_name>/insider/')
@app.route('/<string:ticker_name>/insider/')
@format_response('insiders.html')
def insiders(ticker_name: str):
    ticker = Ticker.get(Ticker.name == ticker_name)
    trades = (
        select_insider_trades()
            .where(InsiderTrade.ticker == ticker)
    )
    response = {
        'ticker_name': ticker_name,
        'trades': patch_insider_hrefs(list(map(model_to_dict, trades)), flask.request.base_url)
    }
    return flask.jsonify(response)


@app.route('/api/<string:ticker_name>/insider/<string:insider_name>/')
@app.route('/<string:ticker_name>/insider/<string:insider_name>/')
@format_response('insider_trades.html')
def insider_trades(ticker_name: str, insider_name):
    ticker = Ticker.get(Ticker.name == ticker_name)
    insider_data = InsiderData.parse(insider_name)
    insider = Insider.get(
        Insider.name == insider_data.name,
        Insider.nasdaq_id == insider_data.nasdaq_id
    )
    trades = (
        select_insider_trades()
            .where((InsiderTrade.ticker == ticker) & (InsiderTrade.insider == insider))
    )
    response = {
        'ticker_name': ticker_name,
        'insider_name': insider_data.name,
        'trades': list(map(model_to_dict, trades))
    }
    return flask.jsonify(response)
