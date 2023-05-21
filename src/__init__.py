from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy 


db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bambu.db"
app.config['SECRET_KEY'] = '57eea008c38612d210670283'
db.init_app(app)

from src import routes
