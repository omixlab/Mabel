from flask import Flask, render_template
import streamlit as st

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/articles_extractor/")
def articles_extractor():
    # return render_template('systematic_review.html')
    return render_template("articles_extractor.html")


if __name__ == "__main__":
    app.run(debug = True )
