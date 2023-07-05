from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, SelectField, BooleanField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from src.models import Users
import src.utils.dicts_tuples.basic_tuple as basic_tuples


class RegisterForm(FlaskForm):
    def validate_username(self, check_user):
        user = Users.query.filter_by(name=check_user.data).first()
        if user:
            raise ValidationError("User already exists! Register another user name.")

    def validate_email(self, check_email):
        email = Users.query.filter_by(email=check_email.data).first()
        if email:
            raise ValidationError(
                "E-mail already exists! Register another user E-mail."
            )

    def validate_password(self, check_password):
        password = Users.query.filter_by(password=check_password.data).first()
        if password:
            raise ValidationError(
                "Password already exists! Register another user Password."
            )

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


class LoginForm(FlaskForm):
    email = StringField(label="E-mail:", validators=[Email(), DataRequired()])
    password = PasswordField(label="Senha:", validators=[DataRequired()])
    submit = SubmitField(label="Log In")

class SearchArticles(FlaskForm):
    option =RadioField('label', choices=[('value','Basic'),('value_two','Advanced')])
    tags = SelectField('option', choices = basic_tuples.tags)
    keyword = StringField(label="Keyword:", validators=[Length(min=2, max=30)])
    connective = SelectField('connective', choices = [(1, 'AND'), (2, 'OR'), (3, 'NOT')])
    open_access = BooleanField('open_access')
    pubmed_query = TextAreaField('pubmed_query', render_kw={'rows':'4', 'cols':'100'})
    elsevier_query = TextAreaField('elsevier_query', render_kw={'rows':'4', 'cols':'100'})
    submit = SubmitField(label="Search")
    check_pubmed = BooleanField('check_pubmed')
    check_scopus = BooleanField('scopus')
    check_elsevier = BooleanField('elsevier')

