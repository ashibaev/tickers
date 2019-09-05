from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from fill_database.html_parsers.base_parser import BaseParser
from common.utils import InsiderTradesField


class InsiderParser(BaseParser):
    INSIDER_URL = 'https://www.nasdaq.com/quotes/insiders/'  # TODO: Какое-то говно?

    @classmethod
    def _process_element(cls, index: int, tag: Tag) -> Any:
        if index == InsiderTradesField.INSIDER:
            tag: Tag = tag.find('a')
            return tag.attrs.get('href')[len(InsiderParser.INSIDER_URL):]
        value = super()._process_element(index, tag)
        if index in [InsiderTradesField.RELATION_TYPE,
                     InsiderTradesField.TRANSACTION_TYPE,
                     InsiderTradesField.OWNER_TYPE]:
            return value.lower()
        if index == InsiderTradesField.LAST_DATE:
            return BaseParser.parse_date(value)
        if index in [InsiderTradesField.SHARES_HELD,
                     InsiderTradesField.SHARES_TRADED,
                     InsiderTradesField.LAST_PRICE]:
            return BaseParser.parse_numeric(value)
        return value

    @classmethod
    def _get_table(cls, data: str) -> Tag:
        return BeautifulSoup(data, features="html.parser").find('div', attrs={'class': 'genTable'}).find('table')
