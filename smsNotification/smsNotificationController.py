from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import smsNotification

app = Flask(__name__)
CORS(app)


@app.route("/listedSMS", methods=['POST'])
def send_listed_sms():
    to_number = request.json['phone']
    message = "your listing " + \
        request.json['listing_id'] + " has been created"
    smsNotification.send_sms(to_number, message)


@app.route("/requestedSMS", methods=['POST'])
def send_requested_sms():
    to_number = request.json['phone']
    message = "There is a new request for your listing " + \
        request.json['listing_id']
    smsNotification.send_sms(to_number, message)


@app.route("/requestedSMS", methods=['POST'])
def send_approved_sms():
    to_number = request.json['phone']
    message = "Your request" + request.json['listing_id'] + "has been approved"
    smsNotification.send_sms(to_number, message)


if __name__ == "__main__":
    app.run(debug=True)