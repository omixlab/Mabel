from src import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=40), nullable=False, unique=True)
    email = db.Column(db.String(length=40), nullable=False, unique=True)
    password = db.Column(db.String(length=300), nullable=False, unique=True)

    def __repr__(self):
        return f"Register: {self.name}"


class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    NCBI_API_KEY = db.Column(db.String(length=36), nullable=False, unique=True)
    X_ELS_APIKey = db.Column(db.String(length=32), nullable=False, unique=True)
    X_ELS_Insttoken = db.Column(db.String(length=32), nullable=False, unique=True)
    user = db.Column(db.Integer, db.ForeignKey("users.id"))
