from flask import flash, redirect, render_template, url_for, request
from src.models import Users
from flask_login import login_required, login_user, logout_user

from src import app, db
from src.forms import LoginForm, RegisterForm, SearchArticles, SearchQuery
from src.utils.extractor import Extractor, query_constructor, execute



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
            #query = Extractor(form.pubmed_query.data, form.elsevier_query.data, form.range_pubmed.data)
            data_tmp = execute.delay(
                #query.keyword,
                form.pubmed_query.data,
                form.elsevier_query.data,
                form.check_pubmed.data,
                form.check_scopus.data,
                form.check_scidir.data,
                form.range_pubmed.data,
                form.range_scopus.data,
                form.range_scidir.data,
            )
            if data_tmp.get() == "None database selected":
                flash(
                    f"Your result id is: {data_tmp}, *but no databases were selected*",
                    category="danger",
                )
            else:
                flash(f"Your result id is: {data_tmp}", category="success")

    if form.errors != {}:
        for err in form.errors.values():
            flash(f"Error user register {err}", category="danger")
    return render_template("articles_extractor.html", form=form, query_form=query_form)


@app.route("/articles_extractor_str/")
@login_required
def articles_extractor_str():
    return render_template("articles_extractor_str.html")

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
