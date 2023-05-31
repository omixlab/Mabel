from flask import Flask, render_template
import streamlit as st
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bambu.db"
db.init_app(app)

class Register(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(length=40), nullable=False, unique=True)
    email = db.Column(db.String(length = 40), nullable= False, unique= True)
    password = db.Column(db.String(length = 300), nullable=False, unique=True)

    def __repr__(self):
        return f'Register: {self.name}'

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/articles_extractor/")
def articles_extractor():
    # return render_template('systematic_review.html')
    return render_template("articles_extractor.html")


if __name__ == "__main__":
    app.run(debug = True )
