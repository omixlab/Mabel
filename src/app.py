from flask import Flask, render_template
import streamlit as st

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/systematic_review/")
def systematic_review():
    # return render_template('systematic_review.html')
    st.set_page_config(page_title="My Streamlit App")
    st.write("Hello, world!")


if __name__ == "__main__":
    app.run()
