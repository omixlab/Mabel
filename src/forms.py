from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired


class RegisterForm(FlaskForm):
    name = StringField(
        label="Username:", validators=[Length(min=2, max=30), DataRequired()]
    )
    email = StringField(label="E-mail:", validators=[Email(), DataRequired()])
    password = PasswordField(
        label="Password:", validators=[Length(min=6), DataRequired()]
    )
    password_conf = PasswordField(
        label="Confirmation Password", validators=[EqualTo("password"), DataRequired()]
    )
    submit = SubmitField(label="Submit")
