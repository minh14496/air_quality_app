"""Example of a single file flask application that uses and open notify API"""
from flask import Flask, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import requests
# Create Flask application instance
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
DB = SQLAlchemy(app)
# Runs root when we visit "/" endpoint
@app.route("/")
def root():
    astro_data = Astro.query.all()
    return f'{astro_data}'
@app.route("/refresh")
def refresh():
    request = requests.get("http://api.open-notify.org/astros.json")
    astro_python_dict = request.json()
    num_of_astros = astro_python_dict["number"]
    record = Astro(num_astros=num_of_astros, time=datetime.now())
    DB.session.add(record)
    DB.session.commit()
    return redirect("/")
@app.route("/reset_db")
def reset():
    DB.drop_all()
    DB.create_all()
    return redirect("/refresh")
# Creating SQLAlchemy sqlite DB
# Creates Astro table
class Astro(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    num_astros = DB.Column(DB.Integer, nullable=False)
    time = DB.Column(DB.String, nullable=False)
    def __repr__(self):
        return f"# of Astros: {self.num_astros} at {self.time}"