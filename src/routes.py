from src import app
from flask import render_template
from src.models import Users
from src.forms import RegisterForm

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/articles_extractor/")
def articles_extractor():
    #user = Users.query.all()
    # return render_template('systematic_review.html')
    return render_template("articles_extractor.html")

@app.route("/register/")
def register():
    form = RegisterForm()
    return render_template('register.html', form = form)