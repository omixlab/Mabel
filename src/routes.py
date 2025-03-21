import os
import json
import io
import zipfile

from flask import (
    flash,
    redirect,
    render_template,
    url_for,
    current_app,
    request,
    Response,
)
from flask_login import login_required, login_user, logout_user, current_user
from wtforms import BooleanField

import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
from functools import wraps

from src import app, db
from src.models import Users, Results, FlashtextModels, TokensPassword, KeysTokens
from src import forms
import src.utils.extractor as extractor
import resend
from src.utils.openAI_deepseek import deepseek 
import src.utils.query_constructor as query_constructor
import src.utils.dicts_tuples.flasky_tuples as dicts_and_tuples
from src.utils.optional_features import flashtext_model_create
import plotly.graph_objects as go

import bcrypt
import uuid


@app.route("/")
def home():
    return render_template("index.html")


# Modularizando as funções de article_extractor
def extractor_base(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with current_app.app_context():
            search_form = forms.SearchArticles()
            available_entities = forms.ScispacyEntities()
            pubtator_options = forms.PubtatorOptions()

            # Flashtext models
            default_models = forms.FlashtextDefaultModels()

            for model in forms.FlashtextModels.query.filter_by(user_id=current_user.id).all(): 
                setattr(forms.FlashtextUserModels, model.name, BooleanField(model.id))
            user_models = forms.FlashtextUserModels()

            if request.method == "POST":
                # Submit query
                if "submit_query" in request.form:
                    selected_entities = [e.name.upper() for e in available_entities if e.data and e.__class__.__name__ == "BooleanField"]
                    pubtator = [e.name for e in pubtator_options if e.data and e.__class__.__name__ == "BooleanField"]
                    if search_form.flashtext_radio.data == "Keyword":
                        kp = search_form.flashtext_string.data

                    elif search_form.flashtext_radio.data == "Model":
                        selected_default_models = [
                            int("".join(c for c in str(model.label) if c.isdigit()))
                            for model in default_models._fields.values()
                            if model.data and model.__class__.__name__ == "BooleanField"
                        ]
                        selected_user_models = [
                            int("".join(c for c in str(model.label) if c.isdigit()))
                            for model in user_models._fields.values()
                            if model.data and model.__class__.__name__ == "BooleanField"
                        ]
                        kp = selected_default_models + selected_user_models
                    else:
                        kp = None

                    # Tokens
                    user_token = KeysTokens.query.filter_by(user_id=current_user.id).first()
                    if user_token:
                        pubmed_token = user_token.NCBI_API_KEY             
                        elsevier_token = user_token.X_ELS_APIKey
                        insttoken = user_token.X_ELS_Insttoken
                    else:
                        flash("You have not set your tokens yet!", category="danger")
                        return redirect(url_for('register_tokens'))
                        
                            
                    
                    # Celery
                    query_fields = {
                        "pubmed": search_form.query_pubmed.data,
                        "scopus":search_form.query_elsevier.data,
                        "scidir":search_form.query_elsevier.data,
                        "scielo":search_form.query_scielo.data,
                        "pprint":search_form.query_pprint.data,
                    }
                    queries_str_list = ''.join([f"{key.capitalize()}: \"{value}\" \n\n" for key, value in query_fields.items() if value])

                    boolean_fields = {
                        "pubmed": search_form.check_pubmed.data,
                        "scopus": search_form.check_scopus.data,
                        "scidir": search_form.check_scidir.data,
                        "scielo": search_form.check_scielo.data,
                        "pprint": search_form.check_pprint.data,
                    }
                    range_fields = {
                        "pubmed":int(search_form.num_pubmed.data),
                        "scopus":int(search_form.num_scopus.data),
                        "scidir":int(search_form.num_scidir.data),
                        "scielo":int(search_form.num_scielo.data),
                        "pprint":None,
                    }

                    data_tmp = extractor.execute.apply_async((
                        pubmed_token,
                        elsevier_token,
                        insttoken,
                        search_form.job_name.data,
                        query_fields,
                        boolean_fields,
                        range_fields,
                        selected_entities,
                        kp,
                        pubtator
                        )
                    )

                    flash(f"Your result id is: {data_tmp.id}", category="success")
                    results = Results(
                        user_id= current_user.id, 
                        celery_id= data_tmp.id, 
                        job_name= search_form.job_name.data,
                        used_queries= queries_str_list)
                    results.status = 'QUEUED'
                    db.session.add(results)
                    db.session.commit()

            if search_form.errors != {}:
                for err in search_form.errors.values():
                    flash(f"{err}", category="danger")

            # Retornar as variáveis
            return func(
                search_form,
                available_entities,
                default_models,
                user_models,
                pubtator_options,
                *args,
                **kwargs,
            )

    return wrapper

@app.route("/articles_extractor/", methods=["GET", "POST"])
@login_required
@extractor_base
def articles_extractor(search_form, available_entities, default_models, user_models, pubtator_options):
    query_form = forms.BasicQuery()

    # Query constructor
    if request.method == 'POST':
        if 'add_keyword' in request.form:
            search_form.query_pubmed.data, search_form.query_elsevier.data, search_form.query_scielo.data, search_form.query_pprint.data = query_constructor.basic(
                pm_query=search_form.query_pubmed.data, 
                els_query=search_form.query_elsevier.data,
                scielo_query=search_form.query_scielo.data,
                ppr_query=search_form.query_pprint.data,
                tag=query_form.tags.data,
                keyword=query_form.keyword.data,
                boolean=query_form.boolean.data,
                open_access=query_form.open_access.data
            )
            
    return render_template("articles_extractor.html", 
                            query_form = query_form,
                            search_form = search_form,
                            entities = available_entities,
                            default_models = default_models,
                            user_models = user_models,
                            pubtator = pubtator_options,
                            show_queries = True)

@app.route("/articles_extractor_str/", methods=["GET", "POST"])
@login_required
@extractor_base
def articles_extractor_str(search_form, available_entities, default_models, user_models, pubtator_options):
    query_form = forms.AdvancedQuery()
    search_filters = forms.SearchFilters()

    # Query constructor
    if request.method == 'POST':
        if 'pubmed_add_keyword' in request.form:
            search_form.query_pubmed.data = query_constructor.pubmed(
                search_form.query_pubmed.data,
                query_form.tags_pubmed.data,
                query_form.keyword_pubmed.data,
                query_form.boolean_pubmed.data,
            )

        if "elsevier_add_keyword" in request.form:
            search_form.query_elsevier.data = query_constructor.elsevier(
                search_form.query_elsevier.data,
                query_form.tags_elsevier.data,
                query_form.keyword_elsevier.data,
                query_form.boolean_elsevier.data,
                query_form.open_access_elsevier.data,
            )
        
        if 'scielo_add_keyword' in request.form:
            if query_form.start_date_scielo.data and query_form.end_date_scielo.data:
                years_range = range(query_form.start_date_scielo.data, query_form.end_date_scielo.data+1)
            else:
                years_range=None

            search_form.query_scielo.data = query_constructor.scielo(
                search_form.query_scielo.data,
                query_form.tags_scielo.data,
                query_form.keyword_scielo.data,
                query_form.boolean_scielo.data,
                years_range,
            )

        if 'pprint_add_keyword' in request.form:
            search_form.query_pprint.data = query_constructor.preprints(
                search_form.query_pprint.data,
                query_form.tags_pprint.data,
                query_form.keyword_pprint.data,
                query_form.boolean_pprint.data,
                f"{query_form.start_date_pprint.data}-{query_form.end_date_pprint.data}",
            )

        if "apply_filters" in request.form:
            filters_tags = dicts_and_tuples.pm_filters
            available_filters = [getattr(search_filters, field_name) for field_name in dir(search_filters) if isinstance(getattr(search_filters, field_name), BooleanField)]
            selected_filters = [filters_tags[f.name] for f in available_filters if f.data]
            
            search_form.query_pubmed.data = query_constructor.pubmed_filters(
                search_form.query_pubmed.data,
                selected_filters
            )





    return render_template("articles_extractor_str.html",
                            query_form=query_form,
                            search_form=search_form,
                            search_filters=search_filters,
                            entities = available_entities,
                            default_models = default_models,
                            user_models = user_models,
                            pubtator = pubtator_options,
                            )

@app.route("/user_profile", methods=["GET", "POST"])
@login_required
def user_profile():
    form = forms.UserProfile()
    user_info = Users.query.filter_by(id=current_user.id).first()
    user_tokens = KeysTokens.query.filter_by(user_id=current_user.id).first()

    # Show current info
    form.name.data = user_info.name
    form.email.data = user_info.email

    if user_tokens and request.method == "GET":
        form.NCBI_API_KEY.data = user_tokens.NCBI_API_KEY
        form.X_ELS_APIKey.data = user_tokens.X_ELS_APIKey
        form.X_ELS_Insttoken.data = user_tokens.X_ELS_Insttoken
        form.OpenAI.data = user_tokens.OpenAI
    
    if request.method == "POST":
        if form.validate_on_submit: 

            # Update existing existing info
            user_info.name = form.name.data
            user_info.email = form.email.data
            
            if form.new_password.data:
                if len(form.new_password.data) < 6:
                    flash("Password must be at least 6 characters long", category="danger")
                elif form.new_password.data != form.confirm_password.data:
                    flash("New password confirmation field didn't match", category="danger")
                elif user_info.convert_password(password_clean_text=form.old_password.data) == False: 
                    flash("Wrong password!", category="danger")
                else:
                    user_info.password = bcrypt.hashpw(
                        form.new_password.data.encode("utf-8"), bcrypt.gensalt()
                        )
                    
                    resend.api_key = os.getenv("RESEND")
                    resend.Emails.send({
                        "from": "onboarding@resend.dev",
                        "to": f"{form.email.data}",
                        "subject": "Changed Password",
                        "html": f"<b>Hello, "
                    + f"The password of your Bambu Systematic Review account has been changed</b><br><br>"
                    + "If this was not you, please contact us"
                    + "bambuenterprise@gmail.com"
                        })
                    flash("Password changed!", category="success")

            if user_tokens:
                user_tokens.NCBI_API_KEY = form.NCBI_API_KEY.data
                user_tokens.X_ELS_APIKey = form.X_ELS_APIKey.data
                user_tokens.X_ELS_Insttoken = form.X_ELS_Insttoken.data
                user_tokens.OpenAI = form.OpenAI.data
                db.session.commit()
            
            else:
                # Create a new token
                register_token = KeysTokens(
                    user_id=current_user.id,
                    NCBI_API_KEY=form.NCBI_API_KEY.data,
                    X_ELS_APIKey=form.X_ELS_APIKey.data,
                    X_ELS_Insttoken=form.X_ELS_Insttoken.data,
                    OpenAI=form.OpenAI.data
                )
                db.session.add(register_token)
                db.session.commit()

            flash("Account informations updated", category="success")


    return render_template("user_profile.html", form=form, user_info=user_info, user_tokens=user_tokens)

@app.route("/user_area/")
@login_required
def user_area():
    results = Results.query.filter_by(user_id=current_user.id).all()
    return render_template("user_area.html", results=results)

@app.route("/result_view/<result_id>")
@login_required
def result_view(result_id):
    result = Results.query.get(result_id)
    if result:
        df = pd.read_json(result.result_json)
        default_columns = ["Title", "DOI", "Abstract", "Date", "Pages", "Journal", "Authors", "Type", "Affiliations", "PubmedID", "Source"]
        missing_columns = [col for col in df.columns if col not in default_columns]
        ordered_columns = default_columns[:4] + missing_columns + default_columns[4:]
        df = df.reindex(columns=ordered_columns)

        if result.result_count_dfs_json:
            count_dfs = json.loads(result.result_count_dfs_json)
            plots = {}
            for key, value in count_dfs.items():
                df_data = json.loads(value)
                reloaded_df = pd.DataFrame(df_data['data'], columns=df_data['columns'], index=df_data['index'])
                
                if reloaded_df.empty:
                    continue
                if pd.isna(reloaded_df.iloc[0][key]):
                    continue
                
                if reloaded_df.iloc[0][key] == '': # remove row counting empty spaces
                    reloaded_df = reloaded_df.iloc[1:].reset_index(drop=True)

                count_dfs[key] = reloaded_df.to_html(classes="table") # Define df of each term appearance count
                plots[key] = go.Figure([go.Bar(x=reloaded_df.head(15)[key], y=reloaded_df.head(15)['Count'])]).to_html()

        else:
            count_dfs, plots = None, None

        return render_template("result_view.html", df=df, count_dfs=count_dfs, plots=plots)
    
    else:
        flash(f"Invalid ID", category="danger")
        return redirect(url_for("user_area"))

@app.route("/openai_engine/<result_id>", methods=["GET", "POST"])
@login_required
def openai_engine(result_id):
    form = forms.OpenAIForm()
    result = Results.query.get(result_id)
    df = pd.read_json(result.result_json)

    register_token_exist = KeysTokens.query.filter_by(user_id=current_user.id).first()
    
    if register_token_exist :
        key = register_token_exist.OpenRouter_Key
    else:
        register_token_master = KeysTokens.query.filter_by(user_id=1).first()
        key = register_token_master.OpenRouter_Key

    list_doi = []
    if request.method == "POST":
        for getid in request.form.getlist("mycheckbox"):
            list_doi.append(getid)

        abstract_selected = df[df["DOI"].isin(list_doi)][["Abstract"]]

        result = deepseek(key, form.question.data, abstract_selected)

        flash(result)

    return render_template("openai_engine.html", df=df, form=form, result_final=result, result_id=result_id)

@app.route("/download/<result_id>/<selected_df>")
@login_required
def download(result_id, selected_df):
    result = Results.query.get(result_id)
    if result:

        if selected_df == 'summary': # download only summary
            result_df = pd.read_json(result.result_json)

            return Response(
                result_df.to_csv(index=False),
                mimetype="txt/csv",
                headers={"Content-disposition": "attachment; filename=result.csv"},
            )

        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                count_dfs = json.loads(result.result_count_dfs_json)
                for key, value in count_dfs.items(): # append count dfs
                    df_data = json.loads(value)
                    result_df = pd.DataFrame(df_data['data'], columns=df_data['columns'], index=df_data['index'])
                    csv_data = result_df.to_csv(index=False)
                    zf.writestr(f'{key}.csv', csv_data)
                if selected_df == 'all': # append summary
                    result_df = pd.read_json(result.result_json)
                    csv_data = result_df.to_csv(index=False)
                    zf.writestr('summary.csv', csv_data)
        
            zip_buffer.seek(0)
            return Response(
                zip_buffer.getvalue(),
                mimetype='application/zip',
                headers={"Content-disposition": "attachment; filename=result.zip"},
            )

    else:
        flash("Unknow result ID", category='danger')
        url_for(user_area)

@app.route("/delete_record/<id>", methods=["POST"])
@login_required
def delete_record(id):
    result = Results.query.filter_by(celery_id=id).first()
    if current_user.id == result.user_id:
        db.session.delete(result)
        db.session.commit()
        return redirect(url_for("user_area"))

@app.route("/user_models/", methods=["GET", "POST"])
@login_required
def user_models():
    form = forms.CreateFlashtextModel()
    user_models = FlashtextModels.query.filter_by(user_id=current_user.id).all() 

    if form.validate_on_submit():
        tsv_path = os.path.join(
            os.environ.get("UPLOAD_FILES"), secure_filename(f"{form.name.data}.txt")
        )
        form.tsv.data.save(tsv_path)

        print(os.environ.get('FLASHTEXT_USER_MODELS'))

        model_path = os.path.join(
            os.environ.get("FLASHTEXT_USER_MODELS"),
            str(current_user.id),
            secure_filename(f"{form.name.data}.pickle"),
        )
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        flashtext_model_create(name=form.name.data, tsv_file=tsv_path, path=model_path)

        model = FlashtextModels(
            user_id=current_user.id,
            name=form.name.data,
            type=form.type.data,
            path=model_path,
        )
        db.session.add(model)
        db.session.commit()

        flash("Model created succesfully", category="success")
        return redirect(url_for("user_models"))

    if form.errors != {}:
        for err in form.errors.values():
            flash(err, category="danger")

    return render_template("user_models.html", user_models=user_models, form=form)

@app.route("/delete_model/<id>", methods=["POST"])
@login_required
def delete_model(id):
    model = FlashtextModels.query.get(id)
    if current_user.id == model.user_id:
        db.session.delete(model)
        db.session.commit()
        return redirect(url_for("user_models"))

@app.route("/register/", methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        user = Users(
            name=form.name.data, email=form.email.data, password_cryp=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("articles_extractor"))
    if form.errors != {}:
        for err in form.errors.values():
            flash(f"Error user register {err}", category="danger")
    return render_template("register.html", form=form)

@app.route("/register_tokens/", methods=["GET", "POST"])
@login_required
def register_tokens():
    form = forms.RegisterTokensForm()
    user_token = KeysTokens.query.filter_by(user_id=current_user.id).first()

    if form.validate_on_submit():
        if user_token:
            # Update existing token
            user_token.NCBI_API_KEY = form.NCBI_API_KEY.data
            user_token.X_ELS_APIKey = form.X_ELS_APIKey.data
            user_token.X_ELS_Insttoken = form.X_ELS_Insttoken.data
            user_token.OpenRouter_Key = form.OpenRouter_Key.data
            db.session.commit()

            flash('Token updated successfully!')
        else:
            # Create a new token
            register_token = KeysTokens(
                user_id=current_user.id,
                NCBI_API_KEY=form.NCBI_API_KEY.data,
                X_ELS_APIKey=form.X_ELS_APIKey.data,
                X_ELS_Insttoken=form.X_ELS_Insttoken.data,
                OpenRouter_Key=form.OpenRouter_Key.data
            )
            db.session.add(register_token)
            db.session.commit()


            flash('New token registered successfully!')
    
    return render_template("register_tokens.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user_logged = Users.query.filter_by(email=form.email.data).first()
        if user_logged and user_logged.convert_password(
            password_clean_text=form.password.data
        ):
            login_user(user_logged)
            flash(f"Success! You're logged in as: {user_logged.name}", category="success")
            return redirect(url_for("articles_extractor"))
        else:
            flash(f"Wrong email or password. Try again!", category="danger")
    return render_template("login.html", form=form)

@app.route("/recovery_password_form", methods=["GET", "POST"])
def recovery_passwordForm():
    form = forms.RecoveryPasswordForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            uuid_id = str(uuid.uuid1().hex)
            token_password = TokensPassword(
                user_id=user.id,
                token=uuid_id,
                #ajustar
                link=f"localhost:5000/recovery_password/{user.id}/{uuid_id}",
            )
            db.session.add(token_password)
            db.session.commit()

            resend.api_key = os.getenv("RESEND")
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": f"{form.email.data}",
                "subject": "Recovery Password",
                "html": f"<b>Hello, "
               + f"Click here to reset your password {token_password.link}</b><br><br>"
               + "If you habe any questions, contact us "
               + "bambuenterprise@gmail.com"
                })

            flash(f"Success! Your password recovery request was sent to your email: {form.email.data}", category="success")
            return redirect(url_for("login"))
        else:
            flash(f"Account not found, please review your e-mail", category="danger")
    return render_template("recovery_password_form.html", form=form)

@app.route("/recovery_password/<id>/<token>", methods=["GET", "POST"])
def recovery_password(token, id):
    form = forms.RecoveryPassword()
    token_password = TokensPassword.query.filter_by(token=token).first()
    if token_password:
        user = Users.query.filter_by(id=id).first()
        if user and form.validate_on_submit():
            user.password = bcrypt.hashpw(
                form.password.data.encode("utf-8"), bcrypt.gensalt()
            )
            flash(
                f"{user.name}, your password has been changed successfuly",
                category="success",
            )
            db.session.delete(token_password)
            db.session.commit()
            return redirect(url_for("login"))
    else:
        flash(f"Token expired, generate another token", category="danger")
        return redirect(url_for("recovery_passwordForm"))
    return render_template("recovery_password.html", form=form, token=token, id=id)

@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully", category="info")
    return redirect(url_for("home"))
