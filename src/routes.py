from flask import flash, redirect, render_template, url_for, Response
from flask_login import login_required, login_user, logout_user
import pandas as pd

from src import app, db
from src.forms import LoginForm, RegisterForm, SearchArticles
from src.models import Users, Results
from src.utils.extractor import Extractor, execute


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/articles_extractor/", methods=["GET", "POST"])
@login_required
def articles_extractor():
    form = SearchArticles()
    if form.validate_on_submit():
        query = Extractor(form.keyword.data, form.range_pubmed.data)
        data_tmp = execute.delay(
            form.check_pubmed.data,
            form.check_scopus.data,
            form.check_scidir.data,
            query.keyword,
            3,
        )
        if data_tmp.get() == "None database selected":
            flash(
                f"Your result id is: {data_tmp}, *but none database selected*",
                category="danger",
            )
        else:
            flash(f"Your result id is: {data_tmp}", category="success")
            print(data_tmp.id)
            results = Results(
                user_id=1, celery_id=data_tmp.id, result_json=data_tmp.get()
            )
            db.session.add(results)
            db.session.commit()
    if form.errors != {}:
        for err in form.errors.values():
            flash(f"Error user register {err}", category="danger")
    return render_template("articles_extractor.html", form=form)


@app.route("/articles_extractor_str/")
@login_required
def articles_extractor_str():
    return render_template("articles_extractor_str.html")


@app.route("/download/")
@login_required
def download():
    result = Results.query.get(9)
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
