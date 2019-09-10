from common.utils.insider_data import InsiderData
from common.utils.insider_trades_fields import InsiderTradesField
from common.utils.id_cache import IdCache
from common.utils.attr_proxy import AttrProxy
from common.utils.env import env


def make_column(iterable):
    return ((x,) for x in iterable)


def get_index_on(table, columns):
    db = table._meta.database
    table_name = table._meta.table_name
    result = [index for index in db.get_indexes(table_name) if index.columns == columns and index.table == table_name]
    return result[0] if result else None
