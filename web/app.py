from datetime import date

from flask import Flask
from flask.json import JSONEncoder
from flask_bootstrap import Bootstrap
from flask_peewee.db import Database

from common.config import CONFIG
from common.models import init_db, DATABASE
from web import TEMPLATE_FOLDER


class DateJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)


init_db(CONFIG.db)

app = Flask('app', template_folder=TEMPLATE_FOLDER)
Bootstrap(app)
app.json_encoder = DateJSONEncoder

db = Database(app, DATABASE)
