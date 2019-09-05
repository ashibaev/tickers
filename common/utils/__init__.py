from common.utils.insider_data import InsiderData
from common.utils.insider_trades_fields import InsiderTradesField
from common.utils.id_cache import IdCache
from common.utils.attr_proxy import AttrProxy
from common.utils.env import env


def make_column(iterable):
    return ((x,) for x in iterable)
