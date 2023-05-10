from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/systematic_review/")
def systematic_review():
    return render_template('systematic_review.html')
