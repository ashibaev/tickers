import datetime
from typing import List, Tuple, Any, Union

import pytz
from bs4 import BeautifulSoup
from bs4.element import Tag


class BaseElementParser:
    TIMEZONE = pytz.timezone('US/Eastern')

    def parse_row_element(self, index: int, tag: Tag) -> Any:
        return (tag.string or '').strip()

    def parse_date(self, value: str) -> datetime.date:
        if value == '':
            return value
        if '/' in value:
            month, day, year = map(int, value.split('/'))
            return datetime.date(year, month, day)
        return datetime.datetime.now(self.TIMEZONE).date()

    def parse_numeric(self, value: str) -> Union[None, str]:
        if len(value) == 0:
            return None
        return ''.join(value.split(','))


class BaseRowParser:
    def __init__(self, element_parser: BaseElementParser) -> None:
        self.element_parser = element_parser

    def parse_row(self, row: Tag) -> Tuple[Any]:
        return tuple(self.element_parser.parse_row_element(i, tag) for i, tag in enumerate(row.findAll('td')))


class BaseTableFinder:
    def get_table(self, data: str) -> Tag:
        return BeautifulSoup(data).find('table')


class BaseTableParser:
    def __init__(self, row_parser: BaseRowParser, table_finder: BaseTableFinder):
        self.row_parser = row_parser
        self.table_finder = table_finder

    def parse_table(self, data: str) -> List[Tuple[Any]]:
        if not data:
            return []
        table: Tag = self.table_finder.get_table(data)
        table_body: Tag = table.find('tbody') or table
        return list(filter(lambda x: any(x),
                           (self.row_parser.parse_row(row) for row in table_body.findAll('tr', recursive=False))))
