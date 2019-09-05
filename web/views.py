import datetime
from functools import wraps

import flask
from flask import make_response, render_template, url_for
from playhouse.shortcuts import model_to_dict

from web.app import app
from common.models import Ticker, Share, RelationType, TransactionType, OwnerType, InsiderTrade, Insider
from common.utils import InsiderData

__all__ = [
]


def is_api_request():
    return flask.request.path.startswith('/api')


def format_response(template_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if is_api_request():
                return response
            data = response.json
            return make_response(render_template(template_name, **data))

        return wrapper

    return decorator


def build_url(endpoint: str, **params):
    prefix = ''
    if is_api_request():
        endpoint += '_api'
        prefix = f"{flask.request.scheme}://{flask.request.host}"
    return prefix + url_for(endpoint, **params)


@app.route('/api/', endpoint='tickers_api')
@app.route('/')
@format_response('tickers.html')
def tickers() -> flask.Response:
    ticker_names = list(x.name for x in Ticker.select(Ticker.name))
    response = {
        'tickers': [
            {
                'ticker_name': ticker_name,
                'href': build_url('shares', ticker_name=ticker_name)
            }
            for ticker_name in ticker_names
        ]
    }
    return flask.jsonify(response)


@app.route('/api/<string:ticker_name>/', endpoint='shares_api')
@app.route('/<string:ticker_name>/')
@format_response('shares.html')
def shares(ticker_name: str) -> flask.Response:
    ticker = Ticker.get(Ticker.name == ticker_name)
    today = datetime.date.today()   # TODO: Ну, в общем случае тут не так
    three_month_ago = today.replace(month=(today.month - 4) % 12 + 1)
    share_models = (
        Share.select()
            .where(Share.date.between(three_month_ago, today) & (Share.ticker == ticker))
            .order_by(Share.date.desc())
    )
    response = {
        'ticker_name': ticker_name,
        'insiders_href': build_url('insiders', ticker_name=ticker_name),
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


def patch_insider_hrefs(trades, ticker_name):
    for trade in trades:
        insider_name = trade['insider']['name']
        insider_nasdaq_id = trade['insider']['nasdaq_id']
        insider_str = str(InsiderData(insider_name, insider_nasdaq_id))
        trade['insider']['href'] = build_url('insider_trades', ticker_name=ticker_name, insider_name=insider_str)
    return trades


@app.route('/api/<string:ticker_name>/insider/', endpoint='insiders_api')
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
        'trades': patch_insider_hrefs(list(map(model_to_dict, trades)), ticker_name)
    }
    return flask.jsonify(response)


@app.route('/api/<string:ticker_name>/insider/<string:insider_name>/', endpoint='insider_trades_api')
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
            .order_by(InsiderTrade.last_date.desc())
    )
    response = {
        'ticker_name': ticker_name,
        'insider_name': insider_data.name,
        'trades': list(map(model_to_dict, trades))
    }
    return flask.jsonify(response)
