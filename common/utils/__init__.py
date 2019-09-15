from common.utils.insider_data import InsiderData
from common.utils.attr_proxy import AttrProxy
from common.utils.env import env
from common.utils.apply import apply


def make_column(iterable):
    return ((x,) for x in iterable)


def get_index_on(table, columns):
    db = table._meta.database
    table_name = table._meta.table_name
    result = [index for index in db.get_indexes(table_name) if index.columns == columns and index.table == table_name]
    return result[0] if result else None


def init_logging():
    import logging.config

    from common.config import CONFIG, LOGGING_LEVEL

    logging.config.dictConfig(CONFIG.logging)
    if LOGGING_LEVEL == 'DEBUG':
        logger = logging.getLogger('peewee')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
