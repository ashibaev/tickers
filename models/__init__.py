from dataclasses import asdict

from config import DBConfig
from models.models import (
    RelationType,
    TransactionType,
    OwnerType,
    Ticker,
    Share,
    Insider,
    InsiderTrade,
    DATABASE
)


__all__ = [
    'init_db',
    'create_tables',
    'RelationType',
    'TransactionType',
    'OwnerType',
    'Ticker',
    'Share',
    'Insider',
    'InsiderTrade',
    'DATABASE'
]


def init_db(db_config: DBConfig) -> None:
    DATABASE.init(**asdict(db_config))


def create_tables() -> None:
    DATABASE.create_tables([
        RelationType,
        TransactionType,
        OwnerType,
        Ticker,
        Share,
        Insider,
        InsiderTrade,
    ])
