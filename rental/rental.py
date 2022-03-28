from flask import Flask, request, jsonify 
from flask_sqlalchemy import SQLAlchemy 
from os import environ
from flask_cors import CORS

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/user_listing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Rental(db.Model):
    __tablename__ = 'rental' 
    rental_id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)
    renter_id = db.Column(db.Integer, nullable=False)
    rent_start_date = db.Column(db.Date(), nullable=False)
    rent_end_date = db.Column(db.Date(), nullable=False)
    total_price = db.Column(db.Float(precision=2), nullable=False)
    rental_status = db.Column(db.String(), nullable=False)


 
    def __init__(self, listing_id,owner_id, renter_id, rent_start_date, rent_end_date, total_price, rental_status): # constructor in an object oriented approach
        self.owner_id = owner_id
        self.listing_id = listing_id
        self.renter_id = renter_id
        self.rent_start_date = rent_start_date
        self.rent_end_date = rent_end_date
        self.total_price = total_price
        self.rental_status = rental_status

 
    def json(self): #specify the properties of a Book
        return {
            "rental_id": self.rental_id, 
            "listing_id" : self.listing_id,
            "owner_id": self.owner_id, 
            "renter_id": self.renter_id, 
            "rent_start_date": self.rent_start_date,
            "rent_end_date": self.rent_end_date, 
            "total_price": self.total_price, 
            "rental_status": self.rental_status
            
            }

@app.route("/rental")
def get_all(): 
	rental_list = Rental.query.all()
	if len(rental_list):
			return jsonify(
				{
					"code": 200,
					"data": {
						"rentals": [rental.json() for rental in rental_list] 
					}
				}
			)
	return jsonify(
			{ 
				"code": 404,
				"message": "There are no rental."
			}
		), 404

 
@app.route("/rental/<string:rental_id>") 
def find_by_rental_id(rental_id):
    rental = Rental.query.filter_by(rental_id=rental_id).first() 
    if rental:
        return jsonify(
            {
                "code": 200,
                "data": rental.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Rental not found."
        }
    ), 404
 
@app.route("/rental", methods=['POST'])
def create_rental():
    owner_id = request.json.get('owner_id')
    listing_id = request.json.get('listing_id')
    total_price = request.json.get('price')
    renter_id = request.json.get('renter_id')
    rent_start_date = request.json.get('rent_start_date')
    rent_end_date = request.json.get('rent_end_date')

    rental = Rental(owner_id = owner_id, listing_id = listing_id, total_price = total_price, renter_id = renter_id, rent_end_date= rent_end_date , rent_start_date=rent_start_date, rental_status="Pending" )
    try:
        db.session.add(rental) 
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
            "data": rental.json()
        }
    ), 201

@app.route("/rental/<string:rental_id>", methods=['PUT'])
def update_rental(rental_id):
    try:
        rental= Rental.query.filter_by(rental_id=rental_id).first()
        if not rental:
            return jsonify(
                {
                    "code": 404,
                        "data": {
                            "rental_id": rental_id
                        },
                        "message": "Rental not found."
                }
            ), 404
        # update status
        data = request.get_json()
        if data['rental_status']:
            rental.rental_status = data['rental_status']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": rental.json()
                }
            ), 200

    except Exception as e:
        return jsonify(
                {
                    "code": 500,
                    "data": {
                        "rental_id": rental_id
                    },
                    "message": "An error occurred while updating the rental. " + str(e)
                }
            ), 500



if __name__ == '__main__':
    app.run(host ="0.0.0.0", port=5000, debug=True) 
