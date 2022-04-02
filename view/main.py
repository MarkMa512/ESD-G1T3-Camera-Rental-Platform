import traceback
from pyrebase import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, jsonify
# from flask_session import Session
# from firebase_admin import credentials

app = Flask(__name__)       #Initialze flask constructor

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

#initialize firebase
# app.secret_key='YdeGnJFEFp2Cc5v7L8wYy3D4bwZTTeDwQpOkuum9'
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

#Initialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": "",'address':"",'phone':''}

#Login
@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

#Index page
@app.route("/index")
def home():
    if person["is_logged_in"] == True:
        return render_template("index.html", email = person["email"], name = person["name"])
    else:
        return redirect(url_for('login'))

#If someone clicks on login, they are redirected to /result
@app.route("/home", methods = ["POST", "GET"])
def signin():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]

        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            # user=auth.refresh(user['refreshToken'])
            # user_id=user['idToken']
            # session['usr']=user_id

            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            # print(session['usr'])

            #Get the name of the user
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            #Redirect to index page
            return render_template("index.html", email = person["email"], name = person["name"])
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
           
            return render_template("index.html", email = person["email"], name = person["name"])
        else:
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register",methods=['POST', 'GET'])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        addr=result['addr']
        phone=result['phone']
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            # user=auth.refresh(user['refreshToken'])
            # user_id=user['idToken']
            # session['usr']=user_id

            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            person['address']=addr
            person['phone']=phone
            #Append data to the firebase realtime database
            data = {"name": name, "email": email, 'address':addr,'phone':phone}
            db.child("users").child(user["localId"]).set(data)
            #Go to index page
            return render_template("index.html", email = person["email"], name = person["name"])

        except:
            traceback.print_exc
            # dumps(result)
            
    else:
        if person["is_logged_in"] == True:
            return render_template("index.html", email = person["email"], name = person["name"])
        else:
            return redirect(url_for('register'))

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
    user_id=person['uid']
    result=dict(db.child("users").order_by_child('email').equal_to(email).get().val())
    if result: 
        return result[user_id]['phone']
    return jsonify(
            {
                "code": 404,
                "message": "User not found"
            }
        ), 404

if __name__ == "__main__":
    app.run(port=5303,debug=True)
