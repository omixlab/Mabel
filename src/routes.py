from flask import flash, redirect, render_template, url_for, request, Response
import pandas as pd
from flask_login import login_required, login_user, logout_user

from src import app, db
from src.models import Users, Results
from src.forms import LoginForm, RegisterForm, SearchQuery, SearchArticles, AdvancedPubMedQuery, AdvancedElsevierQuery, SearchFilters
import src.utils.extractor as extractor
import src.utils.query_constructor as query_constructor
import src.utils.dicts_tuples.flasky_tuples as dicts_and_tuples

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/articles_extractor/", methods=["GET", "POST"])
@login_required
def articles_extractor():
    query_form = SearchQuery()
    form = SearchArticles()

    if request.method == 'POST':
        if 'add_keyword' in request.form:
            # Query constructor
            form.pubmed_query.data, form.elsevier_query.data = query_constructor.basic(
                form.pubmed_query.data, 
                form.elsevier_query.data,
                query_form.tags.data,
                query_form.keyword.data,
                query_form.connective.data,
                query_form.open_access.data
            )
            
        if 'submit_query' in request.form:
            data_tmp = extractor.execute.apply_async((
                form.pubmed_query.data,
                form.elsevier_query.data,
                form.check_pubmed.data,
                form.check_scopus.data,
                form.check_scidir.data,
                int(form.pm_num_of_articles.data),
                int(form.sc_num_of_articles.data),
                int(form.sd_num_of_articles.data),
                
                {
                form.human.name: form.human.data, 
                form.test.name: form.test.data,
                 })
            )

            #if data_tmp.get() == "None database selected":
            #    flash(
            #        f"Your result id is: {data_tmp}, *but no databases were selected*",
            #        category="danger",
            #    )
            #else:

            flash(f"Your result id is: {data_tmp.id}", category="success")
            results = Results(
                user_id=1, celery_id=data_tmp.id, pubmed_query = form.pubmed_query.data,
                elsevier_query=form.elsevier_query.data)
            results.status = 'QUEUED'
            db.session.add(results)
            db.session.commit()

    if form.errors != {}:
        for err in form.errors.values():
            flash(f"Error user register {err}", category="danger")
    
    return render_template("articles_extractor.html", form=form, query_form=query_form)

@app.route("/articles_extractor_str/", methods=["GET", "POST"])
@login_required
def articles_extractor_str():
    pm_query_form = AdvancedPubMedQuery()
    els_query_form = AdvancedElsevierQuery()
    search_form = SearchArticles()
    search_filters = SearchFilters()

    available_entities = [search_form.genes,
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
                {
                search_form.human.name:search_form.human.data, 
                search_form.test.name: search_form.test.data,
                 })
            )

            flash(f"Your result id is: {data_tmp.id}", category="success")
            results = Results(
                user_id=1, celery_id=data_tmp.id, pubmed_query = search_form.pubmed_query.data,
                elsevier_query=search_form.elsevier_query.data)
            results.status = 'QUEUED'
            db.session.add(results)
            db.session.commit()

    if search_form.errors != {}:
        for err in search_form.errors.values():
            flash(f"Error user register {err}", category="danger")

    return render_template("articles_extractor_str.html", pm_query=pm_query_form, els_query=els_query_form, search_form=search_form, search_filters=search_filters, entities=available_entities)

@app.route("/user_area/")
@login_required
def user_area():
    results = Results.query.all()  
    return render_template("user_area.html", results=results)

@app.route("/result/<result_id>")
@login_required
def result_view(result_id):
    result = Results.query.get(result_id)
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
    print(result)
    if result:
        result_df = pd.read_json(result.result_json)
        return Response(
            result_df.to_csv(),
            mimetype="txt/csv",
            headers={"Content-disposition": "attachment; filename=result.csv"},
        )

@app.route('/delete_record/<id>', methods=['POST']) # ISSO NÃO É NADA SEGURO, NÉ?
@login_required
def delete_record(id):
    result = Results.query.filter_by(celery_id=id).first()
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for('user_area'))

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
