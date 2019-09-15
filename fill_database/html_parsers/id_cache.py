from typing import List, Tuple, Any, Iterable, Dict

from fill_database.html_parsers.fields import InsiderTradeField
from fill_database.html_parsers.parser import ParsedData


class IdCache:
    def __init__(self, tickers: List[str], parsed_data: ParsedData):
        self.tickers = self.get_mapping(tickers)
        self.relation_types = self.get_mapping(parsed_data.get_insider_trades_rows(InsiderTradeField.RELATION_TYPE))
        self.transaction_types = self.get_mapping(
            parsed_data.get_insider_trades_rows(InsiderTradeField.TRANSACTION_TYPE)
        )
        self.owner_types = self.get_mapping(parsed_data.get_insider_trades_rows(InsiderTradeField.OWNER_TYPE))
        self.insiders = self.get_mapping(parsed_data.get_insider_trades_rows(InsiderTradeField.INSIDER))
        self.parsed_data = parsed_data

    def get_ticker_id(self, ticker) -> int:
        return self.tickers.get(ticker, None)

    def get_insider_trades_object(self, index: int, item) -> Any:
        mapping = None
        if index == InsiderTradeField.INSIDER:
            mapping = self.insiders
        if index == InsiderTradeField.RELATION_TYPE:
            mapping = self.relation_types
        if index == InsiderTradeField.OWNER_TYPE:
            mapping = self.owner_types
        if index == InsiderTradeField.TRANSACTION_TYPE:
            mapping = self.transaction_types
        if mapping is None:
            return item
        return mapping.get(item, None)

    def prepare_insider_row(self, row) -> Tuple[Any]:
        return tuple(self.get_insider_trades_object(index, item) for index, item in enumerate(row))

    @staticmethod
    def get_mapping(iterable: Iterable[Any]) -> Dict[Any, int]:
        return dict(
            (x[1], x[0])
            for x in enumerate(sorted(set(iterable)), start=1)
        )
