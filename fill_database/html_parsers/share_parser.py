from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from fill_database.html_parsers.base_parser import BaseTableParser, BaseRowParser, BaseElementParser, BaseTableFinder
from fill_database.html_parsers.fields import ShareField


class ShareElementParser(BaseElementParser):
    def parse_row_element(self, index: int, tag: Tag) -> Any:
        value = super().parse_row_element(index, tag)
        if index == ShareField.DATE:
            return self.parse_date(value)
        return self.parse_numeric(value)


class ShareRowParser(BaseRowParser):
    def __init__(self):
        super().__init__(ShareElementParser())


class ShareTableFinder(BaseTableFinder):
    def get_table(self, data: str) -> Tag:
        return BeautifulSoup(data, features="html.parser").find(id='quotes_content_left_pnlAJAX').find('table')


class ShareTableParser(BaseTableParser):
    def __init__(self):
        super().__init__(ShareRowParser(), ShareTableFinder())
