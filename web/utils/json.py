from datetime import date
from decimal import Decimal

from flask.json import JSONEncoder as DefaultJSONEncoder


class JSONEncoder(DefaultJSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return JSONEncoder.default(self, obj)
