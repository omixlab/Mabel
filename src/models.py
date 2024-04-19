from datetime import datetime
from flask_login import UserMixin
from src import bcrypt, db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(length=40), nullable=False, unique=True)
    email = db.Column(db.String(length=40), nullable=False, unique=True)
    password = db.Column(db.String(length=300), nullable=False, unique=True)

    @property
    def password_cryp(self):
        return self.password_cryp

    @password_cryp.setter
    def password_cryp(self, password_text):
        self.password = bcrypt.generate_password_hash(password_text).decode("utf-8")

    def convert_password(self, password_clean_text):
        return bcrypt.check_password_hash(self.password, password_clean_text)

    def __repr__(self):
        return f"Register: {self.name}"


class KeysTokens(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NCBI_API_KEY = db.Column(db.String(length=200), unique=True)
    X_ELS_APIKey = db.Column(db.String(length=200), unique=True)
    X_ELS_Insttoken = db.Column(db.String(length=200), unique=True)
    GeminiAI = db.Column(db.String(length=200))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String, nullable=True)
    celery_id = db.Column(db.String(length=100), nullable=False)
    job_name = db.Column(db.String())
    used_queries = db.Column(db.String())
    result_json = db.Column(db.String())
    created_date = db.Column(db.DateTime, default=datetime.utcnow())


class FlashtextModels(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_date = db.Column(db.DateTime, default=datetime.utcnow())
    name = db.Column(db.String(64))
    type = db.Column(db.String(24))
    path = db.Column(db.String(255))


class TokensPassword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    token = db.Column(db.String(64), nullable=False, unique=True)
    link = db.Column(db.String(90))
    created_date = db.Column(db.DateTime, default=datetime.utcnow())
    updated_date = db.Column(db.DateTime, default=datetime.utcnow())
