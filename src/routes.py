from flask import flash, redirect, render_template, url_for, request, Response
from flask_login import login_required, login_user, logout_user, current_user
from wtforms import BooleanField

import pandas as pd
import os
from werkzeug.utils import secure_filename

from src import app, db
from src.models import Users, Results, FlashtextModels
from src.forms import LoginForm, RegisterForm, SearchQuery, SearchArticles, AdvancedPubMedQuery, AdvancedElsevierQuery, SearchFilters, FlashtextDefaultModels, FlashtextUserModels, CreateFlashtextModel
import src.utils.extractor as extractor
import src.utils.query_constructor as query_constructor
import src.utils.dicts_tuples.flasky_tuples as dicts_and_tuples
from src.utils.optional_features import flashtext_model_create

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/articles_extractor/", methods=["GET", "POST"])
@login_required
def articles_extractor():
    query_form = SearchQuery()
    search_form = SearchArticles()
    default_models = FlashtextDefaultModels()
    
    for model in FlashtextModels.query.filter_by(user_id=current_user.id).all(): 
        setattr(FlashtextUserModels, model.name, BooleanField(model.id))
    user_models = FlashtextUserModels()

    available_entities = [
                        search_form.amino_acid,
                        search_form.anatomical_system,
                        search_form.cancer,
                        search_form.cell,
                        search_form.cellular_component,
                        search_form.developing_anatomical_structure,
                        search_form.gene_or_gene_product,
                        search_form.immaterial_anatomical_entity,
                        search_form.organ,
                        search_form.organism,
                        search_form.organism_subdivision,
                        search_form.organism_substance,
                        search_form.pathological_formation,
                        search_form.simple_chemical,
                        search_form.tissue]
    

    if request.method == 'POST':
        if 'add_keyword' in request.form:
            # Query constructor
            search_form.pubmed_query.data, search_form.elsevier_query.data = query_constructor.basic(
                search_form.pubmed_query.data, 
                search_form.elsevier_query.data,
                query_form.tags.data,
                query_form.keyword.data,
                query_form.connective.data,
                query_form.open_access.data
            )
            
        if 'submit_query' in request.form:
            selected_entities = [e.name.upper() for e in available_entities if e.data]
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


            data_tmp = extractor.execute.apply_async((
                search_form.pubmed_query.data,
                search_form.elsevier_query.data,
                search_form.check_pubmed.data,
                search_form.check_scopus.data,
                search_form.check_scidir.data,
                int(search_form.pm_num_of_articles.data),
                int(search_form.sc_num_of_articles.data),
                int(search_form.sd_num_of_articles.data),
                selected_entities,
                kp
                )
            )

            #if data_tmp.get() == "None database selected":
            #    flash(
            #        f"Your result id is: {data_tmp}, *but no databases were selected*",
            #        category="danger",
            #    )
            #else:

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
    
    return render_template("articles_extractor.html", search_form=search_form, query_form=query_form, entities=available_entities, default_models=default_models, user_models=user_models)

@app.route("/articles_extractor_str/", methods=["GET", "POST"])
@login_required
def articles_extractor_str():
    query_form = SearchQuery()
    pm_query_form = AdvancedPubMedQuery()
    els_query_form = AdvancedElsevierQuery()
    search_filters = SearchFilters()
    search_form = SearchArticles()
    default_models = FlashtextDefaultModels()

    for model in FlashtextModels.query.filter_by(user_id=current_user.id).all(): 
        setattr(FlashtextUserModels, model.name, BooleanField(model.id))
        user_models = FlashtextUserModels()

    available_entities = [
                        search_form.amino_acid,
                        search_form.anatomical_system,
                        search_form.cancer,
                        search_form.cell,
                        search_form.cellular_component,
                        search_form.developing_anatomical_structure,
                        search_form.gene_or_gene_product,
                        search_form.immaterial_anatomical_entity,
                        search_form.organ,
                        search_form.organism,
                        search_form.organism_subdivision,
                        search_form.organism_substance,
                        search_form.pathological_formation,
                        search_form.simple_chemical,
                        search_form.tissue]

    if request.method == 'POST':
        if 'pm_add_keyword' in request.form:
            search_form.pubmed_query.data = query_constructor.pubmed(
                search_form.pubmed_query.data,
                pm_query_form.fields_pm.data,
                pm_query_form.keyword_pm.data,
                pm_query_form.boolean_pm.data,
            )

        if 'els_add_keyword' in request.form:
            search_form.elsevier_query.data = query_constructor.elsevier(
                search_form.elsevier_query.data,
                els_query_form.fields_els.data,
                els_query_form.keyword_els.data,
                els_query_form.boolean_els.data,
                els_query_form.open_access.data
            )

        if 'apply_filters' in request.form:
            filters_tags = dicts_and_tuples.pm_filters
            available_filters = [
                    search_filters.abstract,
                    search_filters.free_full_text,
                    search_filters.full_text,
                    search_filters.booksdocs,
                    search_filters.clinicaltrial,
                    search_filters.meta_analysis,
                    search_filters.randomizedcontrolledtrial,
                    search_filters.review,
                    search_filters.systematicreview,
                    search_filters.humans,
                    search_filters.animal,
                    search_filters.male,
                    search_filters.female,
                    search_filters.english,
                    search_filters.portuguese,
                    search_filters.spanish,
                    search_filters.data,
                    search_filters.excludepreprints,
                    search_filters.medline,
                    ]
            
            selected_filters = [filters_tags[f.name] for f in available_filters if f.data]
            
            search_form.pubmed_query.data = query_constructor.pubmed_filters(
                search_form.pubmed_query.data,
                selected_filters
            )

        if 'submit_query' in request.form:
            selected_entities = [e.name.upper() for e in available_entities if e.data]
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


            data_tmp = extractor.execute.apply_async((
                search_form.pubmed_query.data,
                search_form.elsevier_query.data,
                search_form.check_pubmed.data,
                search_form.check_scopus.data,
                search_form.check_scidir.data,
                int(search_form.pm_num_of_articles.data),
                int(search_form.sc_num_of_articles.data),
                int(search_form.sd_num_of_articles.data),
                selected_entities,
                kp,
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

    return render_template("articles_extractor_str.html", pm_query=pm_query_form, els_query=els_query_form, search_form=search_form, search_filters=search_filters, entities=available_entities, default_models=default_models, user_models=user_models)
 
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
    form = CreateFlashtextModel()
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
    form = RegisterForm()
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
    form = LoginForm()
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


@app.route("/logout")
def logout():
    logout_user()
    flash("You do logout", category="info")
    return redirect(url_for("home"))
