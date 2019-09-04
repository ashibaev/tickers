from dataclasses import dataclass

from fill_database.loaders.base_loader import BaseLoader, Loader


@dataclass
class ShareLoader(BaseLoader):
    def load(self) -> str:
        response = Loader.get(self.url)
        if response.status_code != 200:
            return ''
        return response.text
