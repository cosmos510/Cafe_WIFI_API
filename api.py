import random
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
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


# HTTP GET - Read Record
@app.route('/random')
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafe = result.scalars().all()
    random_cafe = random.choice(all_cafe)
    return jsonify(cafe={
        # "id": random_cafe.id,
        "name": random_cafe.name,
        "location": random_cafe.location,
        "opening": random_cafe.opening,
        "closing": random_cafe.closing,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "coffee_price": random_cafe.coffee_price,
        "coffee_rating": random_cafe.coffee_rating,
        "wifi_strength": random_cafe.wifi_strength,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "power_socket_availability": random_cafe.power_socket_availability,

    })


@app.route("/all")
def get_all_cafe():
    all_cafes = db.session.query(Cafe).order_by(Cafe.name)
    return jsonify(cafes={cafe.id: cafe.to_dict() for cafe in all_cafes})


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    # Note, this may get more than one cafe per location
    all_cafes = result.scalars().all()
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form
        new_cafe = Cafe(name=data['name'],
                        location=data["location"],
                        adresse=data["adresse"],
                        opening=data["opening"],
                        closing=data["closing"],
                        map_url=data['map_url'],
                        img_url=data["img_url"],
                        coffee_price=data["coffee_price"],
                        coffee_rating=data["coffee_rating"],
                        wifi_strength=data['wifi_strength'],
                        seats=data['seats'],
                        has_toilet=data['has_toilet'],
                        power_socket_availability=data["power_socket_availability"]
                        )
        db.session.add(new_cafe)  # add record to database
        db.session.commit()  # commit add request
    return jsonify({"response": {"success": "Successfully add new data"}})


@app.route("/update-price/<int:cafe_id>", methods=["GET", "POST"])
def update_cafe_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={f"success": f"Successfully update price for the cafe {cafe.name}."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


# HTTP DELETE - Delete Record

@app.route("/report-closed/<int:cafe_id>", methods=["DELETE", "GET", "POST"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == os.environ.get('api_key'):
        cafe = db.get_or_404(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=False, port=5002)
