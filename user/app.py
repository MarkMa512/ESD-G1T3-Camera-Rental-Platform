import firebase_admin
# import pyrebase
import json
from firebase_admin import credentials, auth
from flask import Flask, request

app = Flask(__name__)

cred = credentials.Certificate('key.json')
firebase = firebase_admin.initialize_app(cred)

users = [{'uid': 1, 'name': 'Noah Schairer'}]

@app.route('/api/userinfo')

def userinfo():
    return {'data': users}, 200


@app.route('/api/signup',methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    if email is None or password is None:
        return {'message': 'Error missing email or password'},400
    try:
        user = auth.create_user(
               email=email,
               password=password
        )
        return {'message': f'Successfully created user {user.uid}'},200
    except:
        return {'message': 'Error creating user'},400

if __name__ == '__main__':
    app.run(debug=True)