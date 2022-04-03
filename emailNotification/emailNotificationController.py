from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
# from os import environ
from flask_cors import CORS
import emailNofication

app = Flask(__name__)
CORS(app)


@app.route("/listedEmail", methods=['POST'])
def send_listed_email():
    subject = "Your listing has been created"
    body = "your listing " + request.json['listing_description'] + " has been created"
    to = request.json['email']

    emailNofication.email_alert(subject, body, to)

    return jsonify(
        {
            "code": 200,
            "message": "Email sent"
        }
    )


@app.route("/requestedEmail", methods=['POST'])
def send_requested_email():
    subject = "There is a new request for your listing"
    body = "There is a new request for your listing " + \
        request.json['listing_description']
    to = request.json['email']
    emailNofication.email_alert(subject, body, to)
    return jsonify(
        {
            "code": 200,
            "message": "Email sent"
        }
    )

@app.route("/approvedEmail", methods=['POST'])
def send_approved_email():
    subject = "There your request has been approved"
    body = "Your request" + request.json['listing_description'] + "has been approved"
    to = request.json['email']

    emailNofication.email_alert(subject, body, to)
    return jsonify(
        {
            "code": 200,
            "message": "Email sent"
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0" ,port=5301, debug=True)
