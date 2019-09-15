from typing import List

from common.config.configs import Config, DBConfig, ParserConfig, ShareParserConfig, InsiderParserConfig
from common.utils import env

LOGGING_LEVEL = ['INFO', 'DEBUG']['DEBUG' in env]


def parse_tickers(filename: str) -> List[str]:
    with open(filename, 'r') as f:
        return list(set(line.strip().lower() for line in f.readlines()))


CONFIG = Config(
    db=DBConfig(
        user=env.DB_USER,
        host=env.DB_HOST,
        password=env.DB_PASS,
        database=env.DB_NAME,
        port=env.DB_PORT,
        max_connections=env.DB_MAX_CONNECTIONS
    ),
    parser=ParserConfig(
        tickers=parse_tickers('tickers.txt'),
        share_parser=ShareParserConfig(
            url_template='http://old.nasdaq.com/symbol/{ticker}/historical'
        ),
        insider_parser=InsiderParserConfig(
            url_template='http://old.nasdaq.com/symbol/{ticker}/insider-trades',
            pages=10
        ),
        insider_url='https://old.nasdaq.com/quotes/insiders/'
    ),
    logging={
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)-8s %(name)-15s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': '/var/log/app/app.log',
                'maxBytes': 10485760,
                'backupCount': 3
            }
        },
        'loggers': {
            'fill_db': {
                'handlers': ['file', 'console'],
                'level': LOGGING_LEVEL
            }
        }
    }
)
