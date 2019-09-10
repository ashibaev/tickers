from argparse import ArgumentParser
from typing import List


from fill_database.html_parsers import parse_data
from fill_database.html_parsers.parser import ParsedData
from fill_database.loaders import load_data
from common.models import *
from common.config import CONFIG
from common.utils import IdCache, make_column, get_index_on


def get_thread_nums(args: List[str]):
    parser = ArgumentParser()
    parser.add_argument('threads', type=int)
    return parser.parse_args(args).threads


def prepare_tickers(id_cache: IdCache) -> None:
    (Ticker
        .insert_many(make_column(id_cache.tickers), fields=[Ticker.name])
        .on_conflict_ignore()
        .execute())


def prepare_relation_types(id_cache: IdCache) -> None:
    (RelationType
        .insert_many(make_column(id_cache.relation_types), fields=[RelationType.name])
        .on_conflict_ignore()
        .execute())


def prepare_transaction_types(id_cache: IdCache) -> None:
    (TransactionType
        .insert_many(make_column(id_cache.transaction_types), fields=[TransactionType.name])
        .on_conflict_ignore()
        .execute())


def prepare_insiders(parsed_data):
    (Insider
        .insert_many(sorted(set(parsed_data.get_insiders_data())), fields=[Insider.name, Insider.nasdaq_id])
        .on_conflict_ignore()
        .execute())


def prepare_owner_types(id_cache):
    (OwnerType
        .insert_many(make_column(id_cache.owner_types), fields=[OwnerType.name])
        .on_conflict_ignore()
        .execute())


def prepare_insider_trades(id_cache, parsed_data):
    insider_trades = [
        (id_cache.get_ticker_id(ticker),) + id_cache.prepare_insider_row(row)
        for ticker, ticker_data in parsed_data.items()
        for row in ticker_data.insider_data
    ]
    (InsiderTrade
        .insert_many(
            insider_trades,
            fields=[
                InsiderTrade.ticker, InsiderTrade.insider, InsiderTrade.relation,
                InsiderTrade.last_date, InsiderTrade.transaction_type, InsiderTrade.owner_type,
                InsiderTrade.shares_traded, InsiderTrade.last_price, InsiderTrade.shares_held
            ])
        .on_conflict_ignore()
        .execute())


def prepare_shares(id_cache, parsed_data):
    shares = (
        (id_cache.get_ticker_id(ticker),) + row
        for ticker, ticker_data in parsed_data.items()
        for row in ticker_data.share_data
    )
    (Share
        .insert_many(
            shares,
            fields=[Share.ticker, Share.date, Share.open, Share.high, Share.low, Share.close, Share.volume])
        .on_conflict(
            conflict_constraint=get_index_on(Share, ['ticker_id', 'date']).name,
            preserve=[Share.low, Share.high, Share.close, Share.volume]
        ).execute())


# TODO : подумать над id_cache и parsed_data

def prepare_tables(parsed_data: ParsedData):
    id_cache = IdCache(CONFIG.parser.tickers, parsed_data)

    prepare_tickers(id_cache)
    prepare_relation_types(id_cache)
    prepare_transaction_types(id_cache)
    prepare_owner_types(id_cache)
    prepare_insiders(parsed_data)

    prepare_shares(id_cache, parsed_data)
    prepare_insider_trades(id_cache, parsed_data)


def main(args):
    threads = get_thread_nums(args)
    init_db(CONFIG.db)

    create_tables()

    data = load_data(CONFIG.parser, threads)
    parsed_data = parse_data(data)

    prepare_tables(parsed_data)
