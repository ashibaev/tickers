from fill_database.loaders.base_loader import BaseLoader, Loader


class ShareLoader(BaseLoader):
    def load(self) -> str:
        response = Loader.get(self.url)
        if response.status_code != 200:
            return ''
        return response.text

    def __str__(self):
        return f"ShareLoader({self.url}, {self.ticker})"
