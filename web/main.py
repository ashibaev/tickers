from web.app import app
from web.views import *


def main():
    app.run(host='0.0.0.0', port=5000)
