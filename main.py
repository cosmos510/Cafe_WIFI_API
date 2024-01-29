import requests
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(250), unique=True, nullable=False)
    location = db.Column(db.String(250), nullable=False)
    adresse = db.Column(db.String(250), nullable=False)
    opening = db.Column(db.String(12), nullable=False)
    closing = db.Column(db.String(12), nullable=False)

    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)

    coffee_price = db.Column(db.String(250), nullable=True)
    coffee_rating = db.Column(db.String(5), nullable=True)

    wifi_strength = db.Column(db.String(5), nullable=True)

    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.String, nullable=False)

    power_socket_availability = db.Column(db.String(5), nullable=False)

    # This is a dictionary comprehension function created inside the Cafe class definition.
    # It will be used to turn rows into a dictionary before sending it to jsonify.
    def to_dict(
            self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField("Cafe Location on Google Maps (URL)", validators=[DataRequired(), URL()])
    location = StringField('City', validators=[DataRequired()])
    img_url = StringField("Cafe Image on Google (URL)", validators=[DataRequired(), URL()])
    adresse = StringField('Address', validators=[DataRequired()])
    opening = StringField("Opening Time e.g. 8AM", validators=[DataRequired()])
    closing = StringField("Closing Time e.g. 5:30PM", validators=[DataRequired()])
    coffee_price = StringField("Coffee price", validators=[DataRequired()])
    coffee_rating = SelectField("Coffee Rating", choices=["✘", "☕️", "☕️☕️", "☕️☕️☕️", "☕️☕️☕️☕️", "☕️☕️☕️☕️☕️"],
                                validators=[DataRequired()])
    wifi_strength = SelectField("Wifi Strength Rating", choices=["✘", "💪", "💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪💪"],
                                validators=[DataRequired()])
    power_socket_availability = SelectField("Power Socket Availability",
                                            choices=["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"],
                                            validators=[DataRequired()])
    seats = SelectField("Seat Availability", choices=["✘", "🪑", "🪑🪑", "🪑🪑🪑", "🪑🪑🪑🪑", "🪑🪑🪑🪑🪑"],
                        validators=[DataRequired()])
    has_toilet = SelectField("Toilet Availability", choices=["✘", "✅"],
                             validators=[DataRequired()])

    submit = SubmitField('Submit')


class SearchByLoc(FlaskForm):
    location = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


@app.route("/cafes/<int:index>", methods=["GET", "POST"])
def cafes(index):
    cafes = db.get_or_404(Cafe, index)
    return render_template('cafes.html', all_cafe=cafes)


@app.route("/search", methods=["GET", "POST"])
def search_coffe_loc():
    form = SearchByLoc()
    if form.validate_on_submit():
        rep = requests.get(f"http://127.0.0.1:5002/search?loc={form.location.data}")
        data = rep.json()
        all_cafes = data["cafes"]
        b = 0
        cafe_datas = []
        c = len(all_cafes)
        for cafe in range(c):
            while b != c:
                cafe_data = all_cafes[b]
                cafe_datas.append(cafe_data)
                b = b + 1
        return render_template('result.html', all_cafe=cafe_datas, all_cafes=cafe_data)
    return render_template('search.html', form=form)


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    url = f"http://127.0.0.1:5002/add?"
    form = CafeForm()
    if form.validate_on_submit():
        body = {
            'name': f'{form.name.data}',
            'location': f'{form.location.data}',
            'adresse': f'{form.adresse.data}',
            'opening': f'{form.opening.data}',
            'closing': f'{form.closing.data}',
            'map_url': f'{form.map_url.data}',
            'img_url': f'{form.img_url.data}',
            'coffee_price': f'{form.coffee_price.data}',
            'coffee_rating': f'{form.coffee_rating.data}',
            'wifi_strength': f'{form.wifi_strength.data}',
            'seats': f'{form.seats.data}',
            'has_toilet': f'{form.has_toilet.data}',
            'power_socket_availability': f'{form.power_socket_availability.data}'
        }
        rep = requests.post(url, data=body)
        return redirect(url_for('home'))
    return render_template('add.html', form=form)


if __name__ == '__main__':
    app.run(debug=False, port=5001)
