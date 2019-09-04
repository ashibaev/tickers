from typing import Any

from utils import InsiderTradesField


def get_mapping(iterable):
    return dict(
        (x[1], x[0])
        for x in enumerate(sorted(set(iterable)), start=1)
    )


class IdCache:
    def __init__(self, tickers, parsed_data):
        self.tickers = get_mapping(tickers)
        self.relation_types = get_mapping(parsed_data.get_insider_trades_rows(InsiderTradesField.RELATION_TYPE))
        self.transaction_types = get_mapping(parsed_data.get_insider_trades_rows(InsiderTradesField.TRANSACTION_TYPE))
        self.owner_types = get_mapping(parsed_data.get_insider_trades_rows(InsiderTradesField.OWNER_TYPE))
        self.insiders = get_mapping(parsed_data.get_insider_trades_rows(InsiderTradesField.INSIDER))

    def get_ticker_id(self, ticker) -> int:
        return self.tickers.get(ticker, None)

    def get_insider_trades_object(self, index: int, item) -> Any:
        mapping = None
        if index == InsiderTradesField.INSIDER:
            mapping = self.insiders
        if index == InsiderTradesField.RELATION_TYPE:
            mapping = self.relation_types
        if index == InsiderTradesField.OWNER_TYPE:
            mapping = self.owner_types
        if index == InsiderTradesField.TRANSACTION_TYPE:
            mapping = self.transaction_types
        if mapping is None:
            return item
        return mapping.get(item, None)

    def prepare_insider_row(self, row):
        return tuple(self.get_insider_trades_object(index, item) for index, item in enumerate(row))
