from datetime import date

from flask import Flask
from flask.json import JSONEncoder
from flask_bootstrap import Bootstrap
from flask_peewee.db import Database

from config import CONFIG
from models import init_db, DATABASE


class DateJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)


init_db(CONFIG.db)

app = Flask('app')
Bootstrap(app)
app.json_encoder = DateJSONEncoder

db = Database(app, DATABASE)
