from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

username,password = "eric_schles","1234"
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://"+username+":"+password+"@localhost/backpage_ads"
db = SQLAlchemy(app)

from app import models
