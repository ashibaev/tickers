from utils.insider_data import InsiderData
from utils.insider_trades_fields import InsiderTradesField
from utils.id_cache import IdCache


def make_column(iterable):
    return ((x,) for x in iterable)
