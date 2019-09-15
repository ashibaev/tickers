from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from common.config import CONFIG
from fill_database.html_parsers.base_parser import BaseParser
from fill_database.html_parsers.fields import InsiderTradeField


class InsiderParser(BaseParser):
    @classmethod
    def _process_element(cls, index: int, tag: Tag) -> Any:
        if index == InsiderTradeField.INSIDER:
            tag: Tag = tag.find('a')
            return tag.attrs.get('href')[len(CONFIG.parser.insider_url):]
        value = super()._process_element(index, tag)
        if index in [InsiderTradeField.RELATION_TYPE,
                     InsiderTradeField.TRANSACTION_TYPE,
                     InsiderTradeField.OWNER_TYPE]:
            return value.lower()
        if index == InsiderTradeField.LAST_DATE:
            return BaseParser.parse_date(value)
        if index in [InsiderTradeField.SHARES_HELD,
                     InsiderTradeField.SHARES_TRADED,
                     InsiderTradeField.LAST_PRICE]:
            return BaseParser.parse_numeric(value)
        return value

    @classmethod
    def _get_table(cls, data: str) -> Tag:
        return BeautifulSoup(data, features="html.parser").find('div', attrs={'class': 'genTable'}).find('table')
