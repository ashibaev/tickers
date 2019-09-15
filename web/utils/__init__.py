from typing import Iterable, Dict, Any, List, Callable

from peewee import SQL

from common.utils import InsiderData
from web.utils.api_route import add_api_route, format_response, build_url
from web.utils.params import parse_analytics_request, parse_delta_request


def add_insider_hrefs(distinct_insiders: Iterable[Dict[str, Any]],
                      build_insider_url: Callable[..., str]) -> List[Dict[str, Any]]:
    result = []
    for insider in distinct_insiders:
        nasdaq_id = insider.pop('nasdaq_id')
        insider_str = str(InsiderData(insider['name'], nasdaq_id))
        insider['href'] = build_insider_url(insider_name=insider_str)
        result.append(insider)
    return result


def to_sql(*args):
    return [SQL(arg) for arg in args]
