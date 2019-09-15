import concurrent.futures
import logging

from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict


from common.config.configs import ShareParserConfig, InsiderParserConfig, ParserConfig
from fill_database.loaders import InsiderLoader, ShareLoader
from fill_database.loaders.base_loader import BaseLoader


logger = logging.getLogger('fill_db')


@dataclass
class TickerLoaders:
    share_loader: ShareLoader
    insider_loaders: List[InsiderLoader]


@dataclass
class TickerData:
    share_page: str
    insider_pages: List[str]


def get_loaders_for_ticker(ticker: str,
                           share_config: ShareParserConfig,
                           insider_config: InsiderParserConfig) -> TickerLoaders:
    share_url = share_config.url_template.format(ticker=ticker)
    insider_url = insider_config.url_template.format(ticker=ticker)
    pages = insider_config.pages
    return TickerLoaders(
        ShareLoader(share_url, ticker),
        [InsiderLoader(insider_url, ticker, page) for page in range(1, pages + 1)]
    )


def get_loaders(tickers, share_config, insider_config) -> Dict[str, TickerLoaders]:
    return {
        ticker: get_loaders_for_ticker(ticker, share_config, insider_config)
        for ticker in tickers
    }


def load_data(parser_config: ParserConfig, workers) -> Dict[str, TickerData]:
    loaders = get_loaders(parser_config.tickers, parser_config.share_parser, parser_config.insider_parser)
    future_params: Dict[concurrent.futures.Future, BaseLoader] = dict()
    result: Dict[str, TickerData] = {
        ticker: TickerData('', [])
        for ticker in parser_config.tickers
    }
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for ticker, ticker_loaders in loaders.items():
            future_params[executor.submit(ticker_loaders.share_loader.load)] = ticker_loaders.share_loader
            for loader in ticker_loaders.insider_loaders:
                future_params[executor.submit(loader.load)] = loader
            logger.info(f'Tasks for {ticker} created')
        future: concurrent.futures.Future
        for future in concurrent.futures.as_completed(future_params):
            loader = future_params[future]
            logger.info(f'Task for {loader} completed')
            if isinstance(loader, ShareLoader):
                result[loader.ticker].share_page = future.result()
            if isinstance(loader, InsiderLoader):
                result[loader.ticker].insider_pages.append(future.result())
    return result
