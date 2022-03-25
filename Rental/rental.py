from flask import Flask, request, jsonify 
from flask_sqlalchemy import SQLAlchemy 
from os import environ

 
app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/user_listing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


 
db = SQLAlchemy(app)
 
class Rental(db.Model):
    __tablename__ = 'rental' 

    rental_id = db.Column(db.String(), primary_key=True)
    owner_id = db.Column(db.String(), nullable=False)
    renter_id = db.Column(db.String(), nullable=False)
    rent_start_date = db.Column(db.Date(), nullable=False)
    rent_end_date = db.Column(db.Date(), nullable=False)
    total_price = db.Column(db.Float(precision=2), nullable=False)
    rental_status = db.Column(db.String(), nullable=False)


 
    def __init__(self, rental_id, owner_id, renter_id, rent_start_date, rent_end_date, total_price, rental_status): # constructor in an object oriented approach
        self.rental_id = rental_id
        self.owner_id = owner_id
        self.renter_id = renter_id
        self.rent_start_date = rent_start_date
        self.rent_end_date = rent_end_date
        self.total_price = total_price
        self.rental_status = rental_status

 
    def json(self): #specify the properties of a Book
        return {
            "rental_id": self.rental_id, 
            "owner_id": self.owner_id, 
            "renter_id": self.renter_id, 
            "rent_start_date": self.rent_start_date,
            "rent_end_date": self.rent_end_date, 
            "total_price": self.total_price, 
            "rental_status": self.rental_status
            
            }

 #hello :D
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
 
@app.route("/rental/<string:rental_id>", methods=['POST'])
def create_rental(rental_id):
    if (Rental.query.filter_by(rental_id=rental_id).first() ): 
        return jsonify(
            {
                "code": 400,
                "data": {
                    "rental_id": rental_id
                },
                "message": "Rental already exists."
            }
        ), 400
 
    data = request.get_json()

    rental = Rental(rental_id, **data)
 
    try:
        db.session.add(rental) 
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "rental_id": rental_id
                },
                "message": "An error occurred creating the rental."
            }
        ), 500
 
    return jsonify(
        {
            "code": 201,
            "data": rental.json()
        }
    ), 201


if __name__ == '__main__':
    app.run(port=5000, debug=True) 