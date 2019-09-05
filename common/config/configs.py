from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class DBConfig:
    user: str
    host: str
    password: str
    database: str
    port: int
    max_connections: int


@dataclass
class URLHolder:
    url_template: str


@dataclass
class ShareParserConfig(URLHolder):
    pass


@dataclass
class InsiderParserConfig(URLHolder):
    pages: 10


@dataclass
class ParserConfig:
    tickers: List[str]
    share_parser: ShareParserConfig
    insider_parser: InsiderParserConfig


@dataclass
class Config:
    db: DBConfig
    parser: ParserConfig
    logging: Dict[str, Any]
