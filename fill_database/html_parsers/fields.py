from enum import IntEnum


class InsiderTradeField(IntEnum):
    INSIDER = 0
    RELATION_TYPE = 1
    LAST_DATE = 2
    TRANSACTION_TYPE = 3
    OWNER_TYPE = 4
    SHARES_TRADED = 5
    LAST_PRICE = 6
    SHARES_HELD = 7


class ShareField(IntEnum):
    DATE = 0
    OPEN = 1
    HIGH = 2
    LOW = 3
    CLOSE = 4
    VOLUME = 5
