from fill_database.loaders.base_loader import BaseLoader, Loader


class ShareLoader(BaseLoader):
    def __init__(self, url: str, ticker: str):
        super().__init__(url, ticker, Loader())

    def load(self) -> str:
        response = self.loader.get(self.url)
        if response.status_code != 200:
            return ''
        return response.text

    def __str__(self):
        return f"ShareLoader({self.url}, {self.ticker})"
