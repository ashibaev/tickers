import re

from enum import Enum
from typing import List

from fill_database.loaders.base_loader import BaseLoader, Loader


class LoadingState(Enum):
    NOT_CHECKED = 1
    INCORRECT_PAGE = 2
    CORRECT_PAGE = 3


class InsiderLoader(BaseLoader):
    PATTERN = re.compile(r'rel="canonical" href="((([/a-z]|.)*)(\?page=(?P<page>\d+))?)"')

    def __init__(self, url: str, ticker: str, page: int) -> None:
        self.page = page
        super().__init__(url, ticker, Loader())

    def load(self) -> str:
        chunks: List[str] = []
        checked = LoadingState.NOT_CHECKED
        with self.loader.get(self._get_page_url(), stream=True) as response:
            if response.status_code != 200:
                return ''
            chunk: str
            for chunk in response.iter_content(chunk_size=2048, decode_unicode=True):
                if checked == LoadingState.INCORRECT_PAGE:
                    return ''
                if not chunk:
                    continue
                chunks.append(chunk)
                if checked == LoadingState.NOT_CHECKED:
                    checked = self._check_page(chunks)
        return ''.join(chunks)

    def _check_page(self, chunks: List[str]) -> LoadingState:
        part = ''.join(chunks[-2:])
        match = self.PATTERN.search(part)
        if not match:
            return LoadingState.NOT_CHECKED
        if match.group(1) == self._get_page_url():
            return LoadingState.CORRECT_PAGE
        return LoadingState.CORRECT_PAGE

    def _get_page_url(self) -> str:
        if self.page == 1:
            return self.url
        return f"{self.url}?page={self.page}"

    def __str__(self):
        return f"InsiderLoader({self.url}, {self.ticker}, {self.page})"
