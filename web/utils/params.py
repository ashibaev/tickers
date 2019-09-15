import datetime
from decimal import Decimal
from functools import partial

from flask_restful import reqparse


__all__ = [
    'parse_analytics_request',
    'parse_delta_request'
]


def date_type(date_text):
    return datetime.datetime.strptime(date_text, '%Y-%m-%d')


def create_analytics_request_parser() -> reqparse.RequestParser:
    parser = reqparse.RequestParser()
    parser.add_argument('date_from', required=True, location='args', type=date_type)
    parser.add_argument('date_to', required=True, location='args', type=date_type)

    return parser


def create_delta_request_parser() -> reqparse.RequestParser:
    parser = reqparse.RequestParser()
    parser.add_argument('value', required=True, location='args', type=Decimal)
    parser.add_argument('type', required=True, location='args', choices=('open', 'close', 'high', 'low'))

    return parser


analytics_request_parser = create_analytics_request_parser()
delta_request_parser = create_delta_request_parser()


parse_analytics_request = partial(analytics_request_parser.parse_args, strict=True)
parse_delta_request = partial(delta_request_parser.parse_args, strict=True)
