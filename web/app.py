from flask import Flask
from flask_bootstrap import Bootstrap
from flask_peewee.db import Database

from common.config import CONFIG
from common.models import init_db, DATABASE
from web import TEMPLATE_FOLDER
from web.utils.json import JSONEncoder

init_db(CONFIG.db)

app = Flask('app', template_folder=TEMPLATE_FOLDER)
Bootstrap(app)
app.json_encoder = JSONEncoder
db = Database(app, DATABASE)
