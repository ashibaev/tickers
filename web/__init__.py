import pathlib

from common.utils import init_logging

init_logging()

TEMPLATE_FOLDER = str((pathlib.Path(__file__).parent / 'templates'))
