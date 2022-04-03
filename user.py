import traceback
from pyrebase import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, jsonify
import requests
import os
from flask_session import Session

#Firebase configuration
config = {

  "apiKey": "AIzaSyA79Qipw4RifjZ6bvBxdH59wwFrK3pwmjg",
  "authDomain": "camera-rental-27d28.firebaseapp.com",
  "databaseURL": "https://camera-rental-27d28-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "camera-rental-27d28",
  "storageBucket": "camera-rental-27d28.appspot.com",
  "messagingSenderId": "198594507826",
  "appId": "1:198594507826:web:b5e046244e00397357f82b",
  "measurementId": "G-71JZ1N6ZPH",

}
app = Flask(__name__)       #Initialze flask constructor
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.update(SECRET_KEY=os.urandom(24))
# Session(app)

#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

#Login
@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.clear()
   return redirect(url_for('login'))

global sessionemail
@app.route("/login", methods = ["POST", "GET"])
def signin():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data]
        email = result["email"]
        password = result["pass"]
        session['email']=email
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            userId=user['localId']
            session['id']=userId

            userdetails=dict(db.child('users').child(userId).get().val())
            username=userdetails['name']
            sessionemail=userdetails['email']
            session['name']=username

            return render_template("index.html",name=username,session=sessionemail)
        except:
            traceback.print_exc
        
    return render_template('login.html')

@app.route('/index')
def home():
    try:
        print(session['email'])
        name=session['name']
        return render_template("index.html",name=name)
    except:
        return redirect(url_for('login'))


#If someone clicks on register, they are redirected to /register
@app.route("/register",methods=['POST', 'GET'])
def register():
    if  request.method == "POST":     #Only if data has been posted
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        addr=result['addr']
        phone=result['phone']
        session['name']=name
        sessionemail=email
            
        try:
            user=auth.create_user_with_email_and_password(email, password)
            #Append data to the firebase realtime database
            data = {"name": name, "email": email, 'address':addr,'phone':phone}
            session['id']=user['localId']
            db.child("users").child(user["localId"]).set(data)

            #Go to index page
            return render_template("index.html", name=name, session=sessionemail)
        except:
            traceback.print_exc
    return render_template('signup.html')

# Retrieve all users
@app.route('/user')
def get_all():
    users=db.child('users').get()
    return users.val()

# Find user by email
@app.route('/user/<string:email>')
def find_user(email):
    user=db.child("users").order_by_child('email').equal_to(email).get()
    if user: 
        return user.val()
    return jsonify(
            {
                "code": 404,
                "message": "User not found"
            }
        ), 404

# Retrieve user's phone
@app.route('/userphone/<string:email>')
def get_phone(email):
    userid=session['id']
    result=dict(db.child("users").order_by_child('email').equal_to(email).get().val())
    if result: 
        return result[userid]['phone']
    return jsonify(
            {
                "code": 404,
                "message": "User not found"
            }
        ), 404

if __name__ == "__main__":
    app.run(port=5303,debug=True)
