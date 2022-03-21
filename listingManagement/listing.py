from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/user_listing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Listing(db.Model):
    __tablename__ = 'listing'
    listing_id = db.Column(db.String(), primary_key=True)
    owner_id = db.Column(db.String(), nullable=False)
    brand = db.Column(db.String(), nullable=False)
    model = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    image_url = db.Column(db.String(), nullable=False)
    availabiltity = db.Column(db.Boolean(), nullable=False)
    listing_description = db.Column(db.String(), nullable=False)
    daily_rate = db.Column(db.Float(precision=2), nullable=False)

    def __init__(self, listing_id, owner_id, brand, model, price, image_url, availabiltity, listing_description, daily_rate):
        self.listing_id = listing_id
        self.owner_id = owner_id
        self.brand = brand
        self.model = model
        self.price = price
        self.image_url = image_url
        self.availabiltity = availabiltity
        self.listing_description = listing_description
        self.daily_rate = daily_rate

    def json(self):
        return{
            'listing_id': self.listing_id,
            'owner_id': self.owner_id,
            'brand': self.brand,
            'model': self.model,
            'price': self.price,
            'image_url': self.image_url,
            'availabiltity': self.availabiltity,
            'listing_description': self.listing_description,
            'daily_rate': self.daily_rate
        }


@app.route("/listing")
def get_all():
    listing_list = Listing.query.all()
    if len(listing_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "listings": [list.json() for list in listing_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No listing available"
        }
    )


@app.route("/listing/<string:listing_id>")
def find_by_listing_id(listing_id):
    list = Listing.query.filter_by(listing_id=listing_id).first()
    if list:
        return jsonify(
            {
                "code": 200,
                "data": list.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "list not found"
        }
    ), 404


@app.route("/listing/<string:listing_id>", methods=['POST'])
def create_listing(listing_id):
    if (Listing.query.filter_by(listing_id=listing_id).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "listing_id": listing_id
                },
                "message": "listing already exists."
            }
        ), 404

    data = request.get_json()
    listing = Listing(listing_id, **data)

    try:
        db.session.add(listing)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {"isbn13": listing_id},
                "message": "Error in creating a listing"
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": listing.json()
        }
    ), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
