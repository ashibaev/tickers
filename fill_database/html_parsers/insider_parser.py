from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from common.config import CONFIG
from fill_database.html_parsers.base_parser import BaseTableParser, BaseRowParser, BaseElementParser, BaseTableFinder
from fill_database.html_parsers.fields import InsiderTradeField


class InsiderElementParser(BaseElementParser):
    def parse_row_element(self, index: int, tag: Tag) -> Any:
        if index == InsiderTradeField.INSIDER:
            tag: Tag = tag.find('a')
            return tag.attrs.get('href')[len(CONFIG.parser.insider_url):]
        value = super().parse_row_element(index, tag)
        if index in [InsiderTradeField.RELATION_TYPE,
                     InsiderTradeField.TRANSACTION_TYPE,
                     InsiderTradeField.OWNER_TYPE]:
            return value.lower()
        if index == InsiderTradeField.LAST_DATE:
            return self.parse_date(value)
        if index in [InsiderTradeField.SHARES_HELD,
                     InsiderTradeField.SHARES_TRADED,
                     InsiderTradeField.LAST_PRICE]:
            return self.parse_numeric(value)
        return value


class InsiderRowParser(BaseRowParser):
    def __init__(self):
        super().__init__(InsiderElementParser())


class InsiderTableFinder(BaseTableFinder):
    def get_table(self, data: str) -> Tag:
        return BeautifulSoup(data, features="html.parser").find('div', attrs={'class': 'genTable'}).find('table')


class InsiderTableParser(BaseTableParser):
    def __init__(self):
        super().__init__(InsiderRowParser(), InsiderTableFinder())
