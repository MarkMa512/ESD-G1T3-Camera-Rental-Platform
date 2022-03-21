from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=environ.get('dbURL')
# export dbURL=mysql+mysqlconnector://root@localhost:8889/user_listing
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/user_listing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class List(db.Model):
    __tablename__ = 'listing'

    listing_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullabl=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    image_url = db.Column(db.String(100), nullable =False)
    availability = db.Column(db.Booelan, nullable=False)
    listing_description = db.Column(db.String(100), nullable = False)
    daily_rate = db.Column(db.Integer, nullable= False)


    #initializa variables
    def __init__(self, listing_id, owner_id, brand, model, price, image_url, availability, listing_description, daily_rate):
        self.listing_id=listing_id
        self.owner_id = owner_id
        self.brand=brand
        self.model=model
        self.price=price
        self.image_url=image_url
        self.availability=availability
        self.listing_description=listing_description
        self.daily_rate=daily_rate

    def json(self):
        return {"listing_id":self.listing_id,"owner_id":self.owner_id,"brand":self.brand,"model":self.model,"price":self.price, "image_url":self.image_url,"availability":self.availability,"listing_description":self.listing_description,"daily_rate":self.daily_rate}


@app.route("/listing")
def get_all():
    booklist = Book.query.all()
    if len(booklist):
        return jsonify(
            {
                "code":200,
                "data":{
                    "books":[book.json() for book in booklist]
                }
            }
        )
    #other than 200 you can specify
    return jsonify(
        {
            "code": 404,
            "message": "There are no books."
        }
    )

@app.route("/book/<string:isbn13>")
def find_by_isbn13(isbn13):
    book = Book.query.filter_by(isbn13=isbn13).first()
    #.first() return first book of a list
    if book:
        return jsonify(
            {
                "code": 200,
                "data": book.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Book not found."
        }
    ), 404


@app.route("/book/<string:isbn13>", methods=['POST'])
def create_book(isbn13):
    if(Book.query.filter_by(isbn13=isbn13).first()):
        return jsonify(
            {
                "code":400,
                "data":{
                    "isbn13":isbn13
                },
                "message":"Book already exists."
            }
        ),400
    
    data=request.get_json()
    book=Book(isbn13,**data)
    #**data, contain of body from postman to pass the data

    try:
        db.session.add(book)
        db.session.commit()

    except:
        return jsonify(
            {
                "code":500,
                "data":
                {
                    "isbn13":isbn13
                },
                "message":"An error occured creating the book."
            }
        ),500

    return jsonify(
        {
            "code":201,
            "data":book.json()
        }
    )
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

    #export dbURL=mysql+mysqlconnector://root@localhost:8889/book


