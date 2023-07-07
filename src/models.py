from flask_login import UserMixin

from src import bcrypt, db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
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


class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    NCBI_API_KEY = db.Column(db.String(length=36), nullable=False, unique=True)
    X_ELS_APIKey = db.Column(db.String(length=32), nullable=False, unique=True)
    X_ELS_Insttoken = db.Column(db.String(length=32), nullable=False, unique=True)
    user = db.Column(db.Integer, db.ForeignKey("users.id"))
