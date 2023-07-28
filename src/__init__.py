from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from src.celery_utils import make_celery

db = SQLAlchemy()
login_manager = LoginManager()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bambu.db"
app.config["SECRET_KEY"] = "57eea008c38612d210670283"
celery = make_celery(app)
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please login"
login_manager.login_category = "info"
from src import routes
