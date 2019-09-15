import datetime
from functools import partial
from typing import Dict, Any, Union

from flask import jsonify, Response
from peewee import DoesNotExist, Select, SQL
from playhouse.shortcuts import fn

from common.models import Ticker, Share, InsiderTrade, Insider
from common.utils import InsiderData
from web.app import app, db
from web.utils import (add_api_route, format_response, build_url,
                       parse_analytics_request, parse_delta_request,
                       add_insider_hrefs, to_sql)
from web.utils.model_queries import (create_dumper_with_excluded, select_distinct_nasdaq_id,
                                     select_insider_trades, select_share_periods_with_bounded_difference)

__all__ = [
]


@app.errorhandler(DoesNotExist)
@format_response('error_page.html')
def handle_object_does_not_exist_error(error: DoesNotExist) -> Response:
    name = error.__class__.__name__
    return jsonify({'message': f'{name[:-len("DoesNotExist")]} does not exist.'})


@add_api_route(app, '/')
@format_response('tickers.html')
def tickers() -> Response:
    ticker_names = list(x.name for x in Ticker.select(Ticker.name))
    response = {
        'tickers': [
            dict(ticker_name=ticker_name, href=build_url(shares, ticker_name=ticker_name))
            for ticker_name in ticker_names
        ]
    }
    return jsonify(response)


@add_api_route(app, '/<string:ticker_name>/')
@format_response('shares.html')
def shares(ticker_name: str) -> Response:
    ticker = Ticker.get(Ticker.name == ticker_name)
    today = datetime.date.today()
    three_month_ago = today.replace(month=(today.month - 4) % 12 + 1)
    share_models = (Share.select()
                    .where((Share.ticker == ticker)
                           & Share.date.between(three_month_ago, today))
                    .order_by(Share.date.desc()))
    response = {
        'ticker_name': ticker_name,
        'insiders_href': build_url(insiders, ticker_name=ticker_name),
        'shares': list(map(create_dumper_with_excluded(Share.id, Share.ticker), share_models))
    }
    return jsonify(response)


@add_api_route(app, '/<string:ticker_name>/insider/')
@format_response('insiders.html')
def insiders(ticker_name: str) -> Response:
    ticker = Ticker.get(Ticker.name == ticker_name)
    trades = (select_insider_trades()
              .where(InsiderTrade.ticker == ticker))
    distinct_insiders = select_distinct_nasdaq_id(ticker)
    build_insider_url = partial(build_url, insider_trades, ticker_name=ticker_name)
    response = {
        'ticker_name': ticker_name,
        'insiders': add_insider_hrefs(distinct_insiders.dicts(), build_insider_url),
        'trades': list(trades.dicts())
    }
    return jsonify(response)


@add_api_route(app, '/<string:ticker_name>/insider/<string:insider_name>/')
@format_response('insider_trades.html')
def insider_trades(ticker_name: str, insider_name: str) -> Response:
    ticker = Ticker.get(Ticker.name == ticker_name)
    insider_data = InsiderData.parse(insider_name)
    insider = Insider.get(Insider.nasdaq_id == insider_data.nasdaq_id)
    trades = (select_insider_trades()
              .where((InsiderTrade.ticker == ticker)
                     & (InsiderTrade.insider == insider)))
    response = {
        'ticker_name': ticker_name,
        'insider_name': insider_data.name,
        'trades': list(trades.dicts())
    }
    return jsonify(response)


@add_api_route(app, '/<string:ticker_name>/analytics')
@format_response('analytics.html')
def analytics(ticker_name: str) -> Response:
    params = parse_analytics_request()
    ticker = Ticker.get(Ticker.name == ticker_name)
    share_from = Share.get((Share.ticker == ticker) & (Share.date == params.date_from))
    share_to = Share.get((Share.ticker == ticker) & (Share.date == params.date_to))
    difference = {
        name: getattr(share_to, name) - getattr(share_from, name)
        for name in ('open', 'high', 'low', 'close')
    }
    dump_share = create_dumper_with_excluded(Share.id, Share.ticker, Share.volume)
    response = {
        'ticker_name': ticker_name,
        'share_from': dump_share(share_from),
        'share_to': dump_share(share_to),
        'difference': difference
    }
    return jsonify(response)


def prepare_delta_response(interval_or_none: Union[Share, None],
                           ticker_name: str,
                           value: int,
                           price_type: str) -> Dict[str, Any]:
    response = {
        'ticker_name': ticker_name,
        'delta': value,
        'type': price_type,
        'has_answer': interval_or_none is not None
    }
    if interval_or_none is None:
        return response
    interval = interval_or_none
    response.update({
        'from': {
            'date': interval['date_from'],
            'price': interval['price_from']
        },
        'to': {
            'date': interval['date_to'],
            'price': interval['price_to']
        },
        'difference': interval['difference']
    })
    return response


@add_api_route(app, '/<string:ticker_name>/delta')
@format_response('delta.html')
def delta(ticker_name: str) -> Response:
    params = parse_delta_request()
    ticker = Ticker.get(Ticker.name == ticker_name)

    periods_query = select_share_periods_with_bounded_difference(ticker, params.value, params.type)
    min_day_query = (Select(columns=[fn.min(SQL('min_query.days'))])
                     .from_(periods_query.alias('min_query')))
    columns = to_sql('date_from', 'date_to', 'price_from', 'price_to', 'difference')
    interval_query = (Select(columns=columns)
                      .from_(periods_query)
                      .where(SQL('days') == min_day_query)
                      .order_by(SQL('date_from'), SQL('date_to'))
                      .limit(1)
                      .dicts()
                      .execute(db.database))

    interval_or_none: Union[Share, None] = next(iter(interval_query), None)
    response = prepare_delta_response(interval_or_none, ticker_name, params.value, params.type)
    return jsonify(response)
