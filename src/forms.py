from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class RegisterForm(FlaskForm):
    user = StringField(label='Username:')
    email = StringField(label='E-mail:')
    password = PasswordField(label='Password:')
    password_conf = PasswordField(label='Confirmation Password')
    submit = SubmitField(label= 'Submit')