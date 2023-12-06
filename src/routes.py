import os

from flask import flash, redirect, render_template, url_for, current_app, request, Response
from flask_login import login_required, login_user, logout_user, current_user
from wtforms import BooleanField

import pandas as pd
from werkzeug.utils import secure_filename
from functools import wraps

from src import app, db
from src.models import Users, Results, FlashtextModels, TokensPassword
from src import forms
import src.utils.extractor as extractor
import src.utils.yagmail_utils as yagmail
import src.utils.query_constructor as query_constructor
import src.utils.dicts_tuples.flasky_tuples as dicts_and_tuples
from src.utils.optional_features import flashtext_model_create

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

            # Flashtext models
            default_models = forms.FlashtextDefaultModels()

            for model in forms.FlashtextModels.query.filter_by(user_id=current_user.id).all(): 
                setattr(forms.FlashtextUserModels, model.name, BooleanField(model.id))
            user_models = forms.FlashtextUserModels()


            if request.method == 'POST':
                # Submit query
                if 'submit_query' in request.form:
                    selected_entities = [e.name.upper() for e in available_entities if e.data and e.__class__.__name__ == 'BooleanField']
                    if search_form.flashtext_radio.data == 'Keyword':
                        kp = search_form.flashtext_string.data

                    elif search_form.flashtext_radio.data == 'Model':
                        selected_default_models = [int(''.join(c for c in str(model.label) if c.isdigit())) for model in default_models._fields.values()
                                                if model.data and model.__class__.__name__ == 'BooleanField']
                        selected_user_models = [int(''.join(c for c in str(model.label) if c.isdigit())) for model in user_models._fields.values()
                                                if model.data and model.__class__.__name__ == 'BooleanField']
                        kp = selected_default_models + selected_user_models
                    else:
                        kp = None

                    # Celery
                    query_fields = {
                        "pubmed": search_form.query_pubmed.data,
                        "scopus":search_form.query_elsevier.data,
                        "scidir":search_form.query_elsevier.data,
                        "scielo":search_form.query_scielo.data,
                        "pprint":search_form.query_pprint.data,
                    }
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
                        "pprint":int(search_form.num_pprint.data),
                    }

                    data_tmp = extractor.execute.apply_async((
                        query_fields,
                        boolean_fields,
                        range_fields,
                        selected_entities,
                        kp
                        )
                    )

                    flash(f"Your result id is: {data_tmp.id}", category="success")
                    results = Results(
                        user_id=current_user.id, celery_id=data_tmp.id, pubmed_query = search_form.pubmed_query.data,
                        elsevier_query=search_form.elsevier_query.data)
                    results.status = 'QUEUED'
                    db.session.add(results)
                    db.session.commit()

            if search_form.errors != {}:
                for err in search_form.errors.values():
                    flash(f"{err}", category="danger")

            # Retornar as variáveis
            return func(search_form, available_entities, default_models, user_models, *args, **kwargs)

    return wrapper


@app.route("/articles_extractor/", methods=["GET", "POST"])
@login_required
@extractor_base
def articles_extractor(search_form, available_entities, default_models, user_models):
    query_form = forms.BasicQuery()

    # Query constructor
    if request.method == 'POST':
        if 'add_keyword' in request.form:
            search_form.query_pubmed.data, search_form.query_elsevier.data, search_form.query_scielo.data = query_constructor.basic(
                search_form.query_pubmed.data, 
                search_form.query_elsevier.data,
                search_form.query_scielo.data,
                query_form.tags.data,
                query_form.keyword.data,
                query_form.boolean.data,
                query_form.open_access.data
            )
            
    return render_template("articles_extractor.html", 
                            query_form = query_form,
                            search_form = search_form,
                            entities = available_entities,
                            default_models = default_models,
                            user_models = user_models,)



@app.route("/articles_extractor_str/", methods=["GET", "POST"])
@login_required
@extractor_base
def articles_extractor_str(search_form, available_entities, default_models, user_models):
    pubmed_form = forms.AdvancedPubMedQuery()
    elsevier_form = forms.AdvancedElsevierQuery()
    scielo_form = forms.AdvancedScieloQuery()
    pprint_form = forms.AdvancedPreprintsQuery()
    search_filters = forms.SearchFilters()

    # Query constructor
    if request.method == 'POST':
        if 'pm_add_keyword' in request.form:
            search_form.pubmed_query.data = query_constructor.pubmed(
                search_form.pubmed_query.data,
                pubmed_form.fields_pm.data,
                pubmed_form.keyword_pm.data,
                pubmed_form.boolean_pm.data,
            )

        if "els_add_keyword" in request.form:
            search_form.elsevier_query.data = query_constructor.elsevier(
                search_form.elsevier_query.data,
                elsevier_form.fields_els.data,
                elsevier_form.keyword_els.data,
                elsevier_form.boolean_els.data,
                elsevier_form.open_access.data,
            )
        
        if 'se_add_keyword' in request.form:
            search_form.scielo_query.data = query_constructor.scielo(
                search_form.scielo_query.data,
                scielo_form.fields_se.data,
                scielo_form.keyword_se.data,
                scielo_form.boolean_se.data,
            )

        if 'ppr_add_keyword' in request.form:
            search_form.preprints_query.data = query_constructor.preprints(
                search_form.preprints_query.data,
                pprint_form.keyword_ppr.data,
            )

        if 'apply_filters' in request.form:
            filters_tags = dicts_and_tuples.pm_filters
            available_filters = [getattr(search_filters, field_name) for field_name in dir(search_filters) if isinstance(getattr(search_filters, field_name), BooleanField)]
            selected_filters = [filters_tags[f.name] for f in available_filters if f.data]
            
            search_form.pubmed_query.data = query_constructor.pubmed_filters(
                search_form.pubmed_query.data,
                selected_filters
            )

        forms = {
            "pubmed": pubmed_form,
            "elsevier": elsevier_form,
            "scielo": scielo_form,
            "pprint": pprint_form,
            "search": search_form,
            "filters": search_filters,
            "entities": available_entities,
            "default_models": default_models,
            "user_models": user_models,
        }


    return render_template("articles_extractor_str.html", forms=forms)

@app.route("/user_area/")
@login_required
def user_area():
    results = Results.query.filter_by(user_id=current_user.id).all()
    return render_template("user_area.html", results=results)


@app.route("/result/<result_id>")
@login_required
def result_view(result_id):
    result = Results.query.get(result_id)
    print(result)
    if result:
        df = pd.read_json(result.result_json)
        return render_template("result_view.html", df=df)
    else:
        flash(f"Invalid ID", category="danger")
        return redirect(url_for("user_area"))


@app.route("/download/<result_id>")
@login_required
def download(result_id):
    result = Results.query.get(result_id)
    if result:
        result_df = pd.read_json(result.result_json)
        return Response(
            result_df.to_csv(),
            mimetype="txt/csv",
            headers={"Content-disposition": "attachment; filename=result.csv"},
        )

@app.route('/delete_record/<id>', methods=['POST'])
@login_required
def delete_record(id):
    result = Results.query.filter_by(celery_id=id).first()
    if current_user.id == result.user_id:
        db.session.delete(result)
        db.session.commit()
        return redirect(url_for('user_area'))


@app.route("/user_models/", methods=["GET", "POST"])
@login_required
def user_models():
    form = forms.CreateFlashtextModel()
    user_models = FlashtextModels.query.filter_by(user_id=current_user.id).all() 

    if form.validate_on_submit():
        tsv_path = os.path.join(os.environ.get('UPLOAD_FILES'), secure_filename(f'{form.name.data}.txt'))
        form.tsv.data.save(tsv_path)

        model_path = os.path.join(os.environ.get('FLASHTEXT_USER_MODELS'), str(current_user.id), secure_filename(f'{form.name.data}.pickle'))
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        flashtext_model_create(
            name=form.name.data,
            tsv_file= tsv_path,
            path=model_path
        )

        model = FlashtextModels(
            user_id=current_user.id, 
            name=form.name.data,
            type=form.type.data,
            path=model_path
            )
        db.session.add(model)
        db.session.commit()
        
        flash("Model created succesfully", category="success")
        return redirect(url_for("user_models"))

    if form.errors != {}:
        for err in form.errors.values():
            flash(err, category="danger")

    return render_template('user_models.html', user_models=user_models, form=form)

@app.route('/delete_model/<id>', methods=["POST"])
@login_required
def delete_model(id):
    model = FlashtextModels.query.get(id)
    if current_user.id == model.user_id:
        db.session.delete(model)
        db.session.commit()
        return redirect(url_for('user_models'))


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


@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user_logged = Users.query.filter_by(email=form.email.data).first()
        if user_logged and user_logged.convert_password(
            password_clean_text=form.password.data
        ):
            login_user(user_logged)
            flash(f"Success! Your login is: {user_logged.name}", category="success")
            return redirect(url_for("articles_extractor"))
        else:
            flash(f"User or password it's wrong. Try again!", category="danger")
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
                link=f"localhost:5000/recovery_password/{user.id}/{uuid_id}",
            )
            db.session.add(token_password)
            db.session.commit()
            yagmail.send_mail(
                os.getenv("EMAIL"),
                form.email.data,
                "Recovery Password",
                f"<b>Hello "
                + f"your password can be replace in this link {token_password.link}</b><br><br>"
                + "Some questions cantact us "
                + "bambuenterprise@gmail.com",
            )
            flash(f"Success! We send e-mail to {form.email.data}", category="success")
            return redirect(url_for("login"))
        else:
            flash(f"Email don't found, please review your e-mail", category="danger")
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
                f"{user.name}, your password was changed with successfuly",
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
