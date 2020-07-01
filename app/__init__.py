from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_restful import Api

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
mongo = PyMongo(app)

from app import drugs
