import traceback
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/user_listing'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/user_listing'
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

#try try try try

class Listing(db.Model):
    __tablename__ = 'listing'
    listing_id = db.Column(db.Integer(), primary_key=True)
    owner_id = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    availabiltity = db.Column(db.Integer(11), nullable=False)
    listing_description = db.Column(db.String(1023), nullable=False)
    daily_rate = db.Column(db.Float(precision=2), nullable=False)

    def __init__(self, owner_id, brand, model, price, image_url,  availabiltity, listing_description, daily_rate):
        self.owner_id = owner_id
        self.brand = brand
        self.model = model
        self.price = price
        self.image_url = image_url
        self. availabiltity = availabiltity
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
            "message": "listing not found"
        }
    ), 404


@app.route("/listing", methods=['POST'])
def create_list():
    owner_id = request.json.get('owner_id')
    model = request.json.get('model')
    listing_description = request.json.get('listing_description')
    brand = request.json.get('brand')
    price = request.json.get('price')
    daily_rate = request.json.get('daily_rate')
    availabiltity = request.json.get('availabiltity')
    image_url = request.json.get('image_url')

    listing = Listing(owner_id=owner_id, availabiltity=availabiltity, brand=brand, daily_rate=daily_rate,
                      image_url=image_url, listing_description=listing_description, model=model,  price=price)

    try:
        db.session.add(listing)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the list. " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": listing.json()
        }
    ), 201


@app.route("/listing/<string:listing_id>", methods=['PUT'])
def update_listing(listing_id):
    list = Listing.query.filter_by(listing_id=listing_id).first()
    
    if list:
        data = request.get_json()
        if data['brand']:
            list.brand = data['brand']

        if data['model']:
            list.model = data['model']

        if data['price']:
            list.price = data['price']

        if data['listing_id']:
            list.listing_id = data['listing_id'] 

        if data['daily_rate']:
            list.daily_rate = data['daily_rate']

        if data['listing_description']:
            list.listing_description = data['listing_description']  

        if data['availabiltity']:
            list.availabiltity=int(data['availabiltity'])
        
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "data": list.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "listing_id": listing_id
            },
            "message": "Listing not found."
        }
    ), 404


@app.route("/listing/<string:listing_id>", methods=['DELETE'])
def delete_listing(listing_id):
    listing = Listing.query.filter_by(listing_id=listing_id).first()
    if listing:
        db.session.delete(listing)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "listing_id": listing_id
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "listing_id": listing_id
            },
            "message": "Listing not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(port=5304, debug=True)
