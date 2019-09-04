import os
import pathlib

from config.configs import Config, DBConfig, ParserConfig, ShareParserConfig, InsiderParserConfig

BASE_DIR: pathlib.Path = pathlib.Path(__name__).parent.parent


DB_PASS = os.environ['DB_PASS']
LOGGING_LEVEL = ['INFO', 'DEBUG']['DEBUG' in os.environ]


CONFIG = Config(
    db=DBConfig(
        user='nasdaq_user',
        host='localhost',
        password=DB_PASS,
        database='nasdaq',
        port=5432,
        max_connections=50
    ),
    parser=ParserConfig(
        tickers=['aapl', 'cvx', 'goog'],
        share_parser=ShareParserConfig(
            url_template='http://www.nasdaq.com/symbol/{ticker}/historical'
        ),
        insider_parser=InsiderParserConfig(
            url_template='http://www.nasdaq.com/symbol/{ticker}/insider-trades',
            pages=10
        )
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
                'filename': '/var/log/tickers/app.log',
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
