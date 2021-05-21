"""Example of a single file flask application that uses and open notify API"""
from os import getenv
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
import openaq


# Create Flask application instance
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


DB = SQLAlchemy(app)
API = openaq.OpenAQ()


# Runs root when we visit "/" endpoint
@app.route("/")
def root():
    return render_template(
        "base.html", title="Home",
        records=Record.query.filter(Record.value >= 10).all()
        )
    # return str(Record.query.filter(Record.value >= 10).all())
    


@app.route("/refresh")
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    results = get_results()
    for i, result in enumerate(results):
        record = Record(id=i, datetime=result[0], value=result[1])
        DB.session.add(record)
        DB.session.commit()
    return redirect("/")


@app.route("/cities")
def cities():
    cities = get_cities()
    for i, city in enumerate(cities):
        each_city = City(id=i, city=city)
        DB.session.add(each_city)
        DB.session.commit()
    return render_template(
        "city.html", title="List of city",
        cities=City.query.all()
        )


@app.route("/reset")
def reset():
    DB.drop_all()
    DB.create_all()
    return redirect("/refresh")


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'< Time {self.datetime} --- Value {self.value} >'


class City(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    city = DB.Column(DB.String())

    def __repr__(self) -> str:
        return f'< City {self.city} >'


def get_results():
    """Get date and value from city"""
    _, body = API.measurements(city='Los Angeles', parameter='pm25', limit=100)
    result = []
    for dict in body['results']:
        date = dict['date']['utc']
        value = dict['value']
        result.append((date, value))
    return result


def get_cities():
    """Get cities from api"""
    _, cities = API.cities(limit=1000)
    result = []
    for city in cities['results']:
        result.append(city['city'])
    return result
