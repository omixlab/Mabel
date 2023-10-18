from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerRangeField,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)

# from wtforms.fields import html5 as h5fields
# from wtforms.widgets import html5 as h5widgets
# Sfrom wtforms.widgets import TextArea

from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
    InputRequired,
    Optional,
    NumberRange,
)

import src.utils.dicts_tuples.flasky_tuples as flasky_tuples
from src.models import Users


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

class RecoveryPassword(FlaskForm):
    email = StringField(label="E-mail:", validators=[Email(), DataRequired()])
    submit = SubmitField(label="Log In")

class SearchQuery(FlaskForm):
    tags = SelectField(
        "option", choices=flasky_tuples.tags, validators=[InputRequired()], default=1
    )
    keyword = StringField(label="Keyword:", validators=[Length(min=2)])
    connective = SelectField("connective", choices=flasky_tuples.boolean_operators)
    open_access = BooleanField("open_access", validators=[Optional()], default=False)

class AdvancedPubMedQuery(FlaskForm):
    fields_pm = SelectField(
        "option", choices=flasky_tuples.pm_tags, default=1
    )
    keyword_pm = StringField(label="Keyword:", validators=[Length(min=2)])
    boolean_pm = SelectField("connective", choices=flasky_tuples.boolean_operators)

class AdvancedElsevierQuery(FlaskForm):
    fields_els = SelectField(
        "option", choices=flasky_tuples.els_tags, default=1
    )
    keyword_els = StringField(label="Keywords:", validators=[Length(min=2)])
    boolean_els = SelectField("connective", choices=flasky_tuples.boolean_operators)
    open_access = BooleanField("open_access", validators=[Optional()], default=False)


class SearchArticles(FlaskForm):
    pubmed_query = TextAreaField(
        "pubmed_query", 
        render_kw={"rows": "4", "cols": "100"}, 
        validators=[Optional()]
    )
    elsevier_query = TextAreaField(
        "elsevier_query",
        render_kw={"rows": "4", "cols": "100"},
        validators=[Optional()],
    )

    check_pubmed = BooleanField("check")
    range_pubmed = IntegerRangeField(
        default=25,
        validators=[DataRequired(), NumberRange(min=0, max=5000)],
    )
    pm_num_of_articles = IntegerField(default=25, validators=[DataRequired(), NumberRange(min=1, max=5000, message='Number of articles outside of supported range')])

    check_scopus = BooleanField("scopus")
    range_scopus = IntegerRangeField(
        default=25, 
        validators=[DataRequired(), NumberRange(min=1, max=5000)]
    )
    sc_num_of_articles = IntegerField(default=25, validators=[DataRequired(), NumberRange(min=1, max=5000, message='Number of articles outside of supported range')])

    check_scidir = BooleanField("scidir")
    range_scidir = IntegerRangeField(
        default=25, 
        validators=[DataRequired(), NumberRange(min=1, max=5000)]
    )
    sd_num_of_articles = IntegerField(default=25, validators=[DataRequired(), NumberRange(min=1, max=5000, message='Number of articles outside of supported range')])

    check_genes = BooleanField("genes")