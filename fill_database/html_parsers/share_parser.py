from enum import IntEnum
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from fill_database.html_parsers.base_parser import BaseParser


class ShareFields(IntEnum):
    DATE = 0
    OPEN = 1
    HIGH = 2
    LOW = 3
    CLOSE = 4
    VOLUME = 5


class ShareParser(BaseParser):
    @classmethod
    def _process_element(cls, index: int, tag: Tag) -> Any:
        value = super()._process_element(index, tag)
        if index == ShareFields.DATE:
            return BaseParser.parse_date(value)
        return BaseParser.parse_numeric(value)

    @classmethod
    def _get_table(cls, data: str) -> Tag:
        return BeautifulSoup(data, features="html.parser").find(id='quotes_content_left_pnlAJAX').find('table')
