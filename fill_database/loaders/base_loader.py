from dataclasses import dataclass

import requests


class Loader:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/74.0.3729.169 '
                      'YaBrowser/19.6.2.594 (beta) '
                      'Yowser/2.5 Safari/537.36'
    }

    @staticmethod
    def get(*args, **kwargs):
        if 'headers' not in kwargs:
            kwargs.update(headers=Loader.HEADERS)
        else:
            kwargs['headers'].setdefault('User-Agent', Loader.HEADERS['User-Agent'])
        return requests.get(*args, **kwargs)


@dataclass
class BaseLoader:
    url: str
    ticker: str

    def load(self) -> str:
        raise NotImplemented
