from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import firebase_admin
from firebase_admin import credentials, db, firestore, initialize_app 

# Initialise Flask app
app = Flask(__name__)

# Fetch the service account key JSON file contents
cred = credentials.Certificate('???')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://camera-rental-27d28-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# db = firestore.client()
db = firebase.firestore()
User = db.collection('user')

# db = SQLAlchemy(app)

# class User(db.Model):
#     __tablename__='user_info'

#     user_id=db.Column(db.String(),primary_key=True)
#     user_name=db.Column(db.String(),nullable=False)
#     phone=db.Column(db.Integer,nullable=False)
#     email=db.Column(db.String(),nullable=False)
#     residential_address=db.Column(db.String(),nullable=False)

#     def __init__(self,user_id,user_name,phone,email,residential_address):
#         self.user_id=user_id
#         self.user_name=user_name
#         self.phone=phone
#         self.email=email
#         self.residential_address=residential_address

#     def json(self):
#         return {
#         'user_id': self.user_id,
#         'user_name':self.user_name,
#         'phone':self.phone,
#         'email':self.email,
#         'residential_address':self.residential_address
#         }


@app.route("/user")
def get_all():
    userlist=User.query.all()
    if len(userlist):
        return jsonify(
            {
                "code":200,
                "data":{
                    "users":[user.json() for user in userlist]
                }
            }
        )
    return jsonify(
        {
            "code":404,
            "message":"No user for now."
        }
    ),404
    
@app.route("/user/<string:user_id>")
def find_by_user_id(user_id):
    user= User.query.filter_by(user_id=user_id).first()
 
    if user:
        return jsonify(
            {
                "code": 200,
                "data": user.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found"
        }
    ), 404

@app.route('/user/<string:user_id>',methods=['POST'])
def add_user(user_id):
    if(User.query.filter_by(user_id=user_id).first()):
        return jsonify(
            {
                "code":400,
                "data":{
                    "user_id":user_id
                },
                "message":"User already exisits."
            }
        ),400

    data=request.get_json()
    user=User(user_id,**data)

    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify({
            "code":500,
            "data":{
                "user_id":user_id
            },
            "message":"Error detected when adding user."
        }), 500

    return jsonify({
        "code":200,
        "data":user.json()
    }),201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)