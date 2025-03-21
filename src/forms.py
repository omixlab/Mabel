import os

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    IntegerRangeField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    FileField,
    RadioField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    NumberRange,
    Regexp,
    Optional,
    ValidationError,
)
from flask_wtf.file import FileAllowed

from flask_login import current_user

import src.utils.dicts_tuples.flasky_tuples as flasky_tuples
from src.models import Users, FlashtextModels

# from wtforms.fields import html5 as h5fields
# from wtforms.widgets import html5 as h5widgets
# Sfrom wtforms.widgets import TextArea



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
        #password = Users.query.filter_by(password=check_password.data).first()
        #if password:
        #    raise ValidationError(
        #        "Password already exists! Register another user Password."
        #    )
        pass

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

class UserProfile(FlaskForm):
    name = StringField(label="Username:", validators=[Length(min=4, max=24), DataRequired()])
    email = StringField(label="E-mail:", validators=[Email(), DataRequired()])

    old_password = PasswordField(
        label="Old password:"
    )
    new_password = PasswordField(
        label="New password:"
    )
    confirm_password = PasswordField(
        label="Confirm password:"
    )

    NCBI_API_KEY = StringField(label="NCBI:")
    X_ELS_APIKey = StringField(label="Elsevier API key:")
    X_ELS_Insttoken = StringField(label="Elsevier Institutional token:")
    OpenAI = StringField(label="OpenAI:")
    submit = SubmitField(label="Confirm changes")

class RegisterTokensForm(FlaskForm):
    NCBI_API_KEY = StringField(label="NCBI:")
    X_ELS_APIKey = StringField(label="Elsevier API key:")
    X_ELS_Insttoken = StringField(label="Elsevier Institutional token:")
    OpenRouter_Key = StringField(label="OpenRouter_Key:")
    submit = SubmitField(label="Save")

class RecoveryPasswordForm(FlaskForm):
    email = StringField(label="E-mail:", validators=[Email(), DataRequired()])
    submit = SubmitField(label="Send")

class RecoveryPassword(FlaskForm):
    def validate_password(self, check_password):
        #password = Users.query.filter_by(password=check_password.data).first()
        #if password:
        #    raise ValidationError(
        #        "Password already exists! Register another user Password."
        #    )
        pass

    password = PasswordField(
        label="Password:", validators=[Length(min=6), DataRequired()]
    )
    password_conf = PasswordField(
        label="Confirmation Password", validators=[EqualTo("password"), DataRequired()]
    )
    submit = SubmitField(label="Recovery Password")

class BasicQuery(FlaskForm):
    tags = SelectField("option", choices=flasky_tuples.tags, validators=[InputRequired()], default=1)
    keyword = StringField(label="Keyword:", validators=[Length(min=2)])
    boolean = SelectField("connective", choices=[("AND", "AND"), ("OR", "OR"), ("NOT", "NOT")])
    open_access = BooleanField("open_access", validators=[Optional()], default=False)

class AdvancedQuery(FlaskForm):
    tags_pubmed = SelectField("option", choices=flasky_tuples.pubmed_tags, default=1)
    keyword_pubmed = StringField(label="Keyword:", validators=[Length(min=2)])
    boolean_pubmed = SelectField("connective", choices=[("AND", "AND"), ("OR", "OR"), ("NOT", "NOT")])
    open_access_pubmed = None

    tags_elsevier = SelectField("option", choices=flasky_tuples.elsevier_tags, default=1)
    keyword_elsevier = StringField(label="Keywords:", validators=[Length(min=2)])
    boolean_elsevier = SelectField("connective", choices=[("AND", "AND"), ("OR", "OR"), ("NOT", "NOT")])
    open_access_elsevier = BooleanField("open_access", validators=[Optional()], default=False)

    tags_scielo = SelectField("option", choices=flasky_tuples.scielo_tags, default=1)
    keyword_scielo = StringField(label="Keywords:", validators=[Length(min=2)])
    boolean_scielo = SelectField("connective", choices=[("AND", "AND"), ("OR", "OR"), ("AND NOT", "NOT")])
    start_date_scielo = IntegerField(label="Start date:", validators=[Optional(), NumberRange(min=-4713, max=9999)])
    end_date_scielo = IntegerField(label="End date:", validators=[Optional(), NumberRange(min=-4713, max=9999)])
    open_access_scielo = BooleanField("open_access", validators=[Optional()], default=False)

    tags_pprint = SelectField("option", choices=flasky_tuples.pprint_tags, default=1)
    keyword_pprint = StringField(label="Keywords:", validators=[Length(min=2)])
    boolean_pprint = SelectField("connective", choices=[("and", "AND"), ("or", "OR"), ("and not", "NOT")])
    start_date_pprint = StringField(label="Start date:", validators=[Length(min=2)])
    end_date_pprint = StringField(label="End date:", validators=[Length(min=2)])

    open_access_pprint = None

class SearchArticles(FlaskForm):
    job_name = StringField(label="Job name")

    # QUERY
    query_pubmed = TextAreaField(
        label="Pubmed", 
        render_kw={"rows": "4", "cols": "100"}, 
        validators=[Optional()]
    )
    query_elsevier = TextAreaField(
        "Elsevier",
        render_kw={"rows": "4", "cols": "100"},
        validators=[Optional()],
    )
    query_scielo = TextAreaField(
        "SciElo",
        render_kw={"rows": "4", "cols": "100"},
        validators=[Optional()]
    )
    query_pprint = TextAreaField(
        "Preprints",
        render_kw={"rows": "4", "cols": "100"},
        validators=[Optional()],
    )

    # Check and Range
    check_pubmed = BooleanField("pubmed")
    check_scopus = BooleanField("scopus")
    check_scidir = BooleanField("scidir")
    check_scielo = BooleanField("scielo")
    check_pprint = BooleanField("pprint")


    range_pubmed = IntegerRangeField(
        default=25,
        validators=[DataRequired(), NumberRange(min=0, max=5000)],
    )
    range_scopus = IntegerRangeField(
        default=25, 
        validators=[DataRequired(), NumberRange(min=1, max=5000)]
    )
    range_scidir = IntegerRangeField(
        default=25, 
        validators=[DataRequired(), NumberRange(min=1, max=5000)]
    )
    range_scielo = IntegerRangeField(
        default=25,
        validators=[DataRequired(), NumberRange(min=0, max=5000)],
    )
    range_pprint = None


    num_pubmed = IntegerField(
        default=25,
        validators=[
            DataRequired(),
            NumberRange(min=1, max=5000, message="Number of articles outside of supported range"),
        ])

    num_scopus = IntegerField(
        default=25,
        validators=[
            DataRequired(),
            NumberRange(min=1, max=5000, message="Number of articles outside of supported range"),
        ])

    num_scidir = IntegerField(
        default=25,
        validators=[
            DataRequired(),
            NumberRange(min=1, max=5000, message="Number of articles outside of supported range"),
        ])
    
    num_scielo = IntegerField(
        default=25,
        validators=[
            DataRequired(),
            NumberRange(min=1, max=5000, message="Number of articles outside of supported range"),
        ])

    num_pprint = None
    
    title_pubmed = "Pubmed"
    title_scopus = "Scopus"
    title_scidir = "Science Direct"
    title_scielo = "SciElo"
    title_elsevier = "Elsevier"
    title_pprint = "Preprints"


    # Flashtext options
    flashtext_radio = RadioField("Keyword or Models", choices=[("Keyword", "Specify keywords"), ("Model", "Use a model")])
    flashtext_string = StringField("Keywords")

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

class ScispacyEntities(FlaskForm):
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

class FlashtextDefaultModels(FlaskForm):
    genes_human = BooleanField(1)
    genes_danio_rerio = BooleanField(2)

class FlashtextUserModels(FlaskForm):
    # Apenas cria a classe aqui, atributos são criados durante o acesso (routes.py)
    pass

class CreateFlashtextModel(FlaskForm):
    name = StringField(
        "Name of the model",
        validators=[
            InputRequired("Can't leave empty"),
            Length(max=64, message="Name must be at most 64 characters long"),
            Regexp(
                "^[a-zA-Z_]*$", message="Name can only contain letters or underscores"
            ),
        ],
    )
    type = SelectField("Type", choices=flasky_tuples.scispacy)
    tsv = FileField(
        ".txt file",
        validators=[
            FileAllowed(["txt"], "Only .txt files are allowed"),
            InputRequired(message="File is required"),
        ],
    )
    submit = SubmitField(label="Create model")

class PubtatorOptions(FlaskForm):
    gene = BooleanField("Gene")
    disease = BooleanField("Disease")
    chemical = BooleanField("Chemical")
    variant = BooleanField("Variant")
    species = BooleanField("Species")
    cell_line = BooleanField("Cell line")

class OpenAIForm(FlaskForm):
    question = TextAreaField(
        "Message DeepSeek",
        render_kw={"rows": "4", "cols": "100"},
        validators=[DataRequired()],
    )