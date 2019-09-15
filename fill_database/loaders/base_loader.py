import requests


class Loader:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/74.0.3729.169 '
                      'YaBrowser/19.6.2.594 (beta) '
                      'Yowser/2.5 Safari/537.36'
    }

    def get(self, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs.update(headers=Loader.HEADERS)
        else:
            kwargs['headers'].setdefault('User-Agent', Loader.HEADERS['User-Agent'])
        return requests.get(*args, **kwargs)


class BaseLoader:
    def __init__(self, url: str, ticker: str, loader: Loader) -> None:
        self.url = url
        self.ticker = ticker
        self.loader = loader

    def load(self) -> str:
        raise NotImplemented

    def __str__(self):
        return f"BaseLoader({self.url, self.ticker})"
