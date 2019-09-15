import logging
from argparse import ArgumentParser
from typing import List, Dict

from fill_database.html_parsers import parse_data, IdCache, ParsedData
from fill_database.loaders import load_data, TickerData

from common.models import *
from common.config import CONFIG
from common.utils import make_column, get_index_on, InsiderData

logger = logging.getLogger('fill_db')


def get_thread_nums(args: List[str]):
    parser = ArgumentParser()
    parser.add_argument('threads', type=int)
    return parser.parse_args(args).threads


def fill_tickers(id_cache: IdCache) -> None:
    (Ticker
        .insert_many(make_column(id_cache.tickers), fields=[Ticker.name])
        .on_conflict_ignore()
        .execute())


def fill_relation_types(id_cache: IdCache) -> None:
    (RelationType
        .insert_many(make_column(id_cache.relation_types), fields=[RelationType.name])
        .on_conflict_ignore()
        .execute())


def fill_transaction_types(id_cache: IdCache) -> None:
    (TransactionType
        .insert_many(make_column(id_cache.transaction_types), fields=[TransactionType.name])
        .on_conflict_ignore()
        .execute())


def fill_insiders(id_cache: IdCache) -> None:
    data = (tuple(InsiderData.parse(insider)) for insider in id_cache.parsed_data.get_unique_insiders_info())
    (Insider
        .insert_many(data, fields=[Insider.name, Insider.nasdaq_id])
        .on_conflict_ignore()
        .execute())


def fill_owner_types(id_cache: IdCache) -> None:
    (OwnerType
        .insert_many(make_column(id_cache.owner_types), fields=[OwnerType.name])
        .on_conflict_ignore()
        .execute())


def fill_insider_trades(id_cache: IdCache) -> None:
    insider_trades = [
        (id_cache.get_ticker_id(ticker),) + id_cache.prepare_insider_row(row)
        for ticker, ticker_data in id_cache.parsed_data.items()
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


def fill_shares(id_cache: IdCache) -> None:
    shares = (
        (id_cache.get_ticker_id(ticker),) + row
        for ticker, ticker_data in id_cache.parsed_data.items()
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


def fill_tables(parsed_data: ParsedData):
    id_cache = IdCache(CONFIG.parser.tickers, parsed_data)

    for filling_func in (fill_tickers,
                         fill_relation_types,
                         fill_transaction_types,
                         fill_owner_types,
                         fill_insiders,
                         fill_shares,
                         fill_insider_trades):
        logger.info(f'Start: {filling_func.__name__}')
        filling_func(id_cache)
        logger.info(f'Done: {filling_func.__name__}')


def main(args):
    threads = get_thread_nums(args)

    init_db(CONFIG.db)
    logger.info('Database initialized')

    create_tables()
    logger.info('Tables created')

    logger.info('Loading data...')
    data: Dict[str, TickerData] = load_data(CONFIG.parser, threads)
    logger.info('Data loaded')

    logger.info('Parsing data...')
    parsed_data: ParsedData = parse_data(data)
    logger.info('Data parsed')

    logger.info('Filling database...')
    fill_tables(parsed_data)
    logger.info('Complete')
