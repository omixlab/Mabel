from flask import flash, redirect, render_template, url_for, request, Response
import pandas as pd
from flask_login import login_required, login_user, logout_user

from src import app, db
from src.models import Users, Results
from src.forms import LoginForm, RegisterForm, SearchQuery, SearchArticles, AdvancedPubMedQuery, AdvancedElsevierQuery
from src.utils.extractor import query_constructor, execute

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
            
            form.pubmed_query.data, form.elsevier_query.data = query_constructor(
                form.pubmed_query.data, 
                form.elsevier_query.data,
                query_form.tags.data,
                query_form.keyword.data,
                query_form.connective.data,
                query_form.open_access.data
            )
            
        if 'submit_query' in request.form:
            data_tmp = execute.apply_async((
                form.pubmed_query.data,
                form.elsevier_query.data,
                form.check_pubmed.data,
                form.check_scopus.data,
                form.check_scidir.data,
                int(form.pm_num_of_articles.data),
                int(form.sc_num_of_articles.data),
                int(form.sd_num_of_articles.data),
                form.check_genes.data)
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

@app.route("/articles_extractor_str/")
@login_required
def articles_extractor_str():
    pm_query_form = AdvancedPubMedQuery()
    els_query_form = AdvancedElsevierQuery()
    search_form = SearchArticles()

    if request.method == 'POST':
        pass

    if search_form.errors != {}:
        for err in search_form.errors.values():
            flash(f"Error user register {err}", category="danger")

    return render_template("articles_extractor_str.html", pm_query=pm_query_form, els_query=els_query_form, search_form=search_form)

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
