import datetime
from typing import List, Tuple, Any

import pytz
from bs4 import BeautifulSoup
from bs4.element import Tag

# TODO: SoupStainer


class BaseParser:
    NASDAQ_TIMEZONE = pytz.timezone('US/Eastern')

    @classmethod
    def _process_element(cls, index: int, tag: Tag) -> Any:
        return (tag.string or '').strip()

    @classmethod
    def _get_table(cls, data: str) -> Tag:
        return BeautifulSoup(data).find('table')

    @staticmethod
    def parse_date(value: str) -> datetime.date:
        if '/' in value:
            month, day, year = map(int, value.split('/'))
            return datetime.date(year, month, day)
        return datetime.datetime.now(BaseParser.NASDAQ_TIMEZONE).date()

    @staticmethod
    def parse_numeric(value: str) -> str:
        if len(value) == 0:
            return None
        return ''.join(value.split(','))

    def parse_table(self, data: str) -> List[Tuple[Any]]:
        if not data:
            return []
        table: Tag = self._get_table(data)
        table_body: Tag = table.find('tbody') or table
        return list(filter(
                lambda x: any(x),
                (
                    tuple(self._process_element(i, tag) for i, tag in enumerate(row.findAll('td')))
                    for row in table_body.findAll('tr', recursive=False)
                )
            ))
