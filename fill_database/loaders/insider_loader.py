import re

from dataclasses import dataclass
from enum import Enum

from fill_database.loaders.base_loader import BaseLoader, Loader


class LoadingState(Enum):
    NOT_CHECKED = 1
    INCORRECT_PAGE = 2
    CORRECT_PAGE = 3


@dataclass
class InsiderLoader(BaseLoader):
    page: int

    PATTERN = re.compile(r'rel="canonical" href="((([/a-z]|.)*)(\?page=(?P<page>\d+))?)"')

    def load(self) -> str:
        chunks = []
        checked = LoadingState.NOT_CHECKED
        with Loader.get(self._get_page_url(), stream=True) as response:
            if response.status_code != 200:
                return ''
            for chunk in response.iter_content(chunk_size=2048, decode_unicode=True):
                if checked == LoadingState.INCORRECT_PAGE:
                    return ''
                if not chunk:
                    continue
                chunks.append(chunk)
                if checked == LoadingState.NOT_CHECKED:
                    checked = self._check_page(chunks)
        return ''.join(chunks)

    def _check_page(self, chunks) -> LoadingState:
        part = ''.join(chunks[-2:])
        match = InsiderLoader.PATTERN.search(part)
        if not match:
            return LoadingState.NOT_CHECKED
        if match.group(1) == self._get_page_url():
            return LoadingState.CORRECT_PAGE
        return LoadingState.CORRECT_PAGE

    def _get_page_url(self):
        if self.page == 1:
            return self.url
        return f"{self.url}?page={self.page}"
