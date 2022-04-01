from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

user_url = 'http://user-management:5111/user'
listing_url = "http://localhost:5112/"
image_url = "http://localhost:5000/"
activity_log_url = "http://localhost:5001/"
error_url = "http://localhost:5002/"

@app.route("/createListing", methods=['POST'])
def createListingProcess():
    try:
        listing = request.get_json()
        print("\n creating  a new listing from JSON data", listing)
        result = 
    except Exception as e:
        print(e)
        return jsonify({"message": "Invalid request"}), 400

@app.route("/updateListing", methods=['POST'])
def updateListingProcess():
    