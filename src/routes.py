from src import app
from flask import render_template, redirect, url_for, flash
from src.models import Users
from src.forms import RegisterForm
from src import db

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/articles_extractor/")
def articles_extractor():
    #user = Users.query.all()
    # return render_template('systematic_review.html')
    return render_template("articles_extractor.html")

@app.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Users(
        name = form.name.data, 
        email = form.email.data,
        password = form.password.data
    )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('articles_extractor'))
    if form.errors != {}:
        for err in form.errors.values():
            flash(f'Error user register {err}', category="danger")
    return render_template('register.html', form = form)