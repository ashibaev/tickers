from dataclasses import dataclass
from itertools import chain
from typing import List, Tuple, Dict, Any, Iterable

from fill_database.loaders import TickerData
from fill_database.html_parsers import InsiderParser, ShareParser
from common.utils import InsiderData, InsiderTradesField


@dataclass
class ParsedTickerData:
    share_data: List[Tuple[str]]
    insider_data: List[Tuple[str]]


class ParsedData(Dict[str, ParsedTickerData]):
    def get_insider_trades_rows(self, column: int = None) -> Iterable[Any]:
        return (
            x if column is None else x[column]
            for parsed_ticker_data in self.values()
            for x in parsed_ticker_data.insider_data
        )

    def get_insiders_data(self):
        return (
            tuple(InsiderData.parse(insider))
            for insider in self.get_insider_trades_rows(InsiderTradesField.INSIDER)
        )


def parse_data(data: Dict[str, TickerData]) -> ParsedData:
    share_parser = ShareParser()
    insider_parser = InsiderParser()
    return ParsedData(
        (ticker, ParsedTickerData(
            share_parser.parse_table(ticker_data.share_page),
            list(chain.from_iterable([insider_parser.parse_table(page) for page in ticker_data.insider_pages]))
        ))
        for ticker, ticker_data in data.items()
    )
