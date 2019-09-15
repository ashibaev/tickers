from dataclasses import dataclass
from itertools import chain
from typing import List, Tuple, Dict, Any, Iterable, Callable

from fill_database.html_parsers.fields import InsiderTradeField
from fill_database.loaders import TickerData
from fill_database.html_parsers import InsiderTableParser, ShareTableParser
from common.utils import apply


@dataclass
class ParsedTickerData:
    share_data: List[Tuple[str]]
    insider_data: List[Tuple[str]]


def sorted_unique(f: Callable[..., Iterable[Any]]) -> Callable[..., Iterable[Any]]:
    return apply(sorted)(apply(set)(f))


class ParsedData(Dict[str, ParsedTickerData]):
    @sorted_unique
    def get_unique_relation_types(self) -> Iterable[str]:
        return self.get_insider_trades_rows(InsiderTradeField.RELATION_TYPE)

    @sorted_unique
    def get_unique_owner_types(self) -> Iterable[str]:
        return self.get_insider_trades_rows(InsiderTradeField.OWNER_TYPE)

    @sorted_unique
    def get_unique_transaction_types(self) -> Iterable[str]:
        return self.get_insider_trades_rows(InsiderTradeField.TRANSACTION_TYPE)

    @sorted_unique
    def get_unique_insiders_info(self) -> Iterable[str]:
        return self.get_insider_trades_rows(InsiderTradeField.INSIDER)

    def get_insider_trades_rows(self, column: int) -> Iterable[Any]:
        return (
            x[column]
            for parsed_ticker_data in self.values()
            for x in parsed_ticker_data.insider_data
        )


def parse_data(data: Dict[str, TickerData]) -> ParsedData:
    share_parser = ShareTableParser()
    insider_parser = InsiderTableParser()
    return ParsedData(
        (ticker, ParsedTickerData(
            share_parser.parse_table(ticker_data.share_page),
            list(chain.from_iterable([insider_parser.parse_table(page) for page in ticker_data.insider_pages]))
        ))
        for ticker, ticker_data in data.items()
    )
