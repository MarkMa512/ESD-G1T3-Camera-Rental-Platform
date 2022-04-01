from pyrebase import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, jsonify

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
  "measurementId": "G-71JZ1N6ZPH"
}

#initialize firebase
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

#Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("welcome.html", email = person["email"], name = person["name"])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    person['is_logged_in']=False
    return redirect(url_for('signup'))

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            #Get the name of the user
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            #Redirect to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
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
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            person['address']=addr
            person['phone']=phone
            #Append data to the firebase realtime database
            data = {"name": name, "email": email,'address':addr,'phone':phone}
            db.child("users").child(user["localId"]).set(data)
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('register'))
#            return jsonify({
#                "code":500,
#                "message":"Error detected when adding user."
#            }), 500
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))

@app.route('/user_info')
def user_info():
    token=session['user']
    user=auth.get_account_info(token)
    print(user)
    return render_template('welcome.html')

# Retrieve all users
@app.route('/user')
def get_all():
    users=db.child('users').get()
    if len(users):
        return users
    return jsonify(
            {
                "code":404,
                "message":"No user for now."
            }
        ),404

# Find user by id
@app.route('/user/<string:uid>')
def find_user(uid):
    user=db.child("users").child(uid).get()
    if user:
        return user.val()
    return jsonify(
            {
                "code": 404,
                "message": "User not found"
            }
        ), 404


if __name__ == "__main__":
    app.run(debug=True)
