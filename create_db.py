from src import app
from src import db
with app.app_context():
    db.create_all()
