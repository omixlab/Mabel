import os

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
    FileField
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
    Regexp,
)
from flask_wtf.file import FileAllowed

from flask_login import current_user

import src.utils.dicts_tuples.flasky_tuples as flasky_tuples
from src.models import Users, FlashtextModels


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

    # SciSpacy entities
    amino_acid = BooleanField("AMINO_ACID")
    anatomical_system = BooleanField("ANATOMICAL_SYSTEM")
    cancer = BooleanField("CANCER")
    cell = BooleanField("CELL")
    cellular_component = BooleanField("CELLULAR_COMPONENT")
    developing_anatomical_structure = BooleanField("DEVELOPING_ANATOMICAL_STRUCTURE")
    gene_or_gene_product = BooleanField("GENE_OR_GENE_PRODUCT")
    immaterial_anatomical_entity = BooleanField("IMMATERIAL_ANATOMICAL_ENTITY")
    multi_tissue_structure = BooleanField("MULTI-TISSUE_STRUCTURE")
    organ = BooleanField("ORGAN")
    organism = BooleanField("ORGANISM")
    organism_subdivision = BooleanField("ORGANISM_SUBDIVISION")
    organism_substance = BooleanField("ORGANISM_SUBSTANCE")
    pathological_formation = BooleanField("PATHOLOGICAL_FORMATION")
    simple_chemical = BooleanField("SIMPLE_CHEMICAL")
    tissue = BooleanField("TISSUE")

    # Flashtext options
    flashtext_radio = RadioField("Keyword or Models", choices=[("Keyword", "Specify keywords"), ("Model", "Use a model")])
    flashtext_string = StringField("Keywords", name="aaa", description="bbb")


class SearchFilters(FlaskForm):
    abstract = BooleanField("Abstract")
    free_full_text = BooleanField("Free full text")
    full_text = BooleanField("Full text")
    booksdocs = BooleanField("Books and documents")
    clinicaltrial = BooleanField("Clinical trial")
    meta_analysis = BooleanField("Meta-Analysis")
    randomizedcontrolledtrial = BooleanField("Randomized Controlled Trial")
    review = BooleanField("Review")
    systematicreview = BooleanField("Systematic Review")
    humans = BooleanField("Humans")
    animal = BooleanField("Other Animals")
    male = BooleanField("Male")
    female = BooleanField("Female")
    english = BooleanField("English")
    portuguese = BooleanField("Portuguese")
    spanish = BooleanField("Spanish")
    data = BooleanField("Associated data")
    excludepreprints = BooleanField("Exclude preprints")
    medline = BooleanField("MEDLINE")


class FlashtextDefaultModels(FlaskForm):
    genes_human = BooleanField("genes_human")
    genes_danio_rerio = BooleanField("genes_danio_rerio")

class FlashtextUserModels(FlaskForm):
    pass

class CreateFlashtextModel(FlaskForm):
    name = StringField("Name of the model", validators=[InputRequired("Can't leave empty"), Length(max=64, message='Name must be at most 64 characters long'), Regexp('^[a-zA-Z_]*$', message='Name can only contain letters or underscores')])
    type = SelectField("Type", choices=flasky_tuples.scispacy)
    tsv = FileField(".txt file", validators=[FileAllowed(['txt'], "Only .txt files are allowed"), InputRequired(message='File is required')])
    submit = SubmitField(label="Create model")
