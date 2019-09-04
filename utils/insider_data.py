from typing import NamedTuple


class InsiderData(NamedTuple):
    name: str
    nasdaq_id: int

    @staticmethod
    def parse(value: str):
        name, nasdaq_id = value.rsplit('-', 1)
        nasdaq_id = int(nasdaq_id)
        name = ' '.join(map(lambda x: x.upper(), name.split('-')))
        return InsiderData(name, nasdaq_id)

    def __str__(self):
        return '-'.join(self.name.lower().split() + [str(self.nasdaq_id)])
