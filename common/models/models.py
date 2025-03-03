from functools import partial

from peewee import (
    Check,
    CharField,
    DecimalField,
    ForeignKeyField,
    IntegerField,
    Model,
    DateField,
    SQL)

from playhouse.pool import PooledPostgresqlExtDatabase

DATABASE = PooledPostgresqlExtDatabase(None)


class BaseModel(Model):
    class Meta:
        database = DATABASE
        legacy_table_names = False


MoneyField = partial(DecimalField, decimal_places=10, max_digits=30)


class RelationType(BaseModel):
    name = CharField(max_length=30, unique=True)


class TransactionType(BaseModel):
    name = CharField(max_length=30, unique=True)


class OwnerType(BaseModel):
    name = CharField(max_length=30, unique=True)


class Ticker(BaseModel):
    name = CharField(max_length=10, unique=True)


class Share(BaseModel):
    ticker = ForeignKeyField(Ticker)
    date = DateField(index=True)
    open = MoneyField(constraints=[Check('open >= 0')])
    high = MoneyField(constraints=[Check('high >= 0')])
    low = MoneyField(constraints=[Check('low >= 0')])
    close = MoneyField(constraints=[Check('close >= 0')])
    volume = IntegerField(constraints=[Check('volume >= 0')])

    class Meta:
        constraints = (
            SQL(f'CONSTRAINT share_unique_idx UNIQUE ("ticker_id", "date")'),
        )


class Insider(BaseModel):
    name = CharField(max_length=40, index=True)
    nasdaq_id = IntegerField(unique=True)

    class Meta:
        indexes = (
            (('name', 'nasdaq_id'), True),
        )


class InsiderTrade(BaseModel):
    ticker = ForeignKeyField(Ticker)
    insider = ForeignKeyField(Insider)
    relation = ForeignKeyField(RelationType)
    last_date = DateField(index=True)
    transaction_type = ForeignKeyField(TransactionType)
    owner_type = ForeignKeyField(OwnerType)
    shares_traded = IntegerField()
    last_price = MoneyField(null=True)
    shares_held = IntegerField()

    class Meta:
        indexes = (
            (('ticker', 'insider'), False),
        )
