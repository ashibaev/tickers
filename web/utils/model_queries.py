from decimal import Decimal
from functools import partial
from typing import List, Callable, Dict, Any

from peewee import Field, Model, ModelSelect, Select, fn
from playhouse.shortcuts import model_to_dict

from common.models import Ticker, InsiderTrade, Insider, RelationType, TransactionType, OwnerType, Share


def create_dumper_with_excluded(*exclude: List[Field]) -> Callable[[Model], Dict[str, Any]]:
    return partial(model_to_dict, exclude=exclude)


def select_share_periods_with_bounded_difference(ticker: Ticker, value: Decimal, price_type: str) -> Select:
    share_table = Share.alias()
    price_from = getattr(Share, price_type)
    price_to = getattr(share_table, price_type)
    difference = fn.abs(price_from - price_to)
    days = share_table.date - Share.date
    return (Share.select(Share.date.alias('date_from'),
                         share_table.date.alias('date_to'),
                         price_from.alias('price_from'),
                         price_to.alias('price_to'),
                         difference.alias('difference'),
                         days.alias('days'))
            .join(share_table, join_type='CROSS')
            .where((Share.ticker == ticker)
                   & (share_table.ticker == ticker)
                   & (Share.date < share_table.date)
                   & (difference >= value)))


def select_distinct_nasdaq_id(ticker: Ticker) -> ModelSelect:
    return (InsiderTrade.select(Insider.name.alias('name'),
                                Insider.nasdaq_id.alias('nasdaq_id'))
            .join_from(InsiderTrade, Insider)
            .where(InsiderTrade.ticker == ticker)
            .order_by(Insider.name)
            .distinct())


def select_insider_trades() -> ModelSelect:
    return (InsiderTrade.select(Insider.name.alias('insider_name'),
                                RelationType.name.alias('relation_name'),
                                InsiderTrade.last_date,
                                TransactionType.name.alias('transaction_type_name'),
                                OwnerType.name.alias('owner_type_name'),
                                InsiderTrade.shares_traded,
                                InsiderTrade.last_price,
                                InsiderTrade.shares_held)
            .join_from(InsiderTrade, RelationType)
            .join_from(InsiderTrade, OwnerType)
            .join_from(InsiderTrade, TransactionType)
            .join_from(InsiderTrade, Insider)
            .order_by(InsiderTrade.last_date.desc()))
