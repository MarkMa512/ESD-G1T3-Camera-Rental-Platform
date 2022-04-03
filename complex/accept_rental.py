from flask import Flask, request, jsonify
from flask_cors import CORS
import json

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

rental_URL = "http://localhost:5305/rental"
listing_URL = "http://localhost:5304/listing"
email_url = "http://localhost:5301/requestedEmail"
sms_url = "http://localhost:5306/requestedSMS"
user_url = "http://localhost:5303/user"    



@app.route("/accept_rental", methods=['POST'])
def accept_rental():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            rental_accept= request.get_json()
            print("\nReceived an rental request in JSON:", rental_accept)

            # do the actual work
            # 1. Send order info {cart items}
            
            rental_address = processGetAddress(rental_accept["address"])
            rental_accept_result = processAcceptRental(rental_accept)
            listing_result = processGetListing(rental_accept_result)
            listing_update_result = processUpdateListing(listing_result)
            return jsonify(listing_update_result,rental_address), listing_update_result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "Place_Rental.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processGetAddress(address):
    print("\n---- INVOKING GET POSTAL CODE MICROSERVICE -------")
    rental2_URL = rental_URL + "/" + address
    postal_code_result = invoke_http(rental2_URL,method="POST", json=address)
    print("postal_code_result", postal_code_result)
    
    return postal_code_result


def processAcceptRental(rental_accept):
    # 2. Send the order info {cart items}
    # Invoke the order microservice
    print("\n-----  Invoking Rental Micro Service ------- ")
    rental2_URL = rental_URL + "/" + str(rental_accept["rental_id"])
    rental_accept_result = invoke_http(rental2_URL, method = "PUT", json = rental_accept)
    print('rental_result:', rental_accept_result)

    code = rental_accept_result["code"]
    message = json.dumps(rental_accept_result)

    if code not in range(200,300):
        print("Error has occurred")
        print(message)

        return {
                "code": 500,
                "data": {"rental_accept_result": rental_accept_result},
                "message": "Rental update failure sent for error handling."
            }
    
    else:
        print("\nRental Accepted Successful ")
        return rental_accept_result


def processGetListing(rental_accept_result):
    print("\n---- INVOKING GET LISTING MICROSERVICE -------")
    print(rental_accept_result)
    listing_id = rental_accept_result["data"]["listing_id"]
    get_listing_url = listing_URL + "/" + str(listing_id)
    listing_details = invoke_http(get_listing_url, method = "GET")
    print("\n---------- LISTING DETAILS -----------", listing_details["data"])

    code = listing_details["code"]
    message = json.dumps(listing_details)

    if code not in range(200,300):
        print("An error has occurred")
        print(message)

        return {
                "code": 500,
                "data": {"Get Listing Result": listing_details},
                "message": "Get Listing failure sent for error handling."
            }
    else:
        print(" Get Listing Successful")
        return listing_details

def processUpdateListing(listing_result):
    print("\n---- INVOKING UPDATE LISTING MICROSERVICE -------")
    tosend = listing_result["data"]
    tosend["availabiltity"] = "0"
    listing_id = tosend["listing_id"]


    listing_url_update = listing_URL + "/" + str(listing_id)
    listing_update_result = invoke_http(listing_url_update, method = "PUT", json = tosend)
    print("\n--------listing_update_result", listing_update_result)

    code = listing_update_result["code"]
    message = json.dumps(listing_update_result)

    if code not in range(200,300):
        print ("An error has occured")
        print(message)

        return {
            "code": 500,
            "data" : {
                "Update Listing Result" : listing_update_result},
                "message" : "Update listing failure sent for error handling."
            }
    else:
        print("Listing Update is successful")
        return listing_update_result
    
    

    # # 4. Record new order
    # print('\n\n-----Invoking activity_log microservice-----')
    # invoke_http(activity_log_URL, method="POST", json=order_result)
    # print("\nOrder sent to activity log.\n")
    # # - reply from the invocation is not used;
    # # continue even if this invocation fails
    # # record the activity log anyway

    # # Check the order result; if a failure, send it to the error microservice.
    # code = order_result["code"]
    # if code not in range(200, 300):
    #     print('\n\n-----Invoking error microservice as order fails-----')
    #     invoke_http(error_URL, method="POST", json=order_result)
    #     # - reply from the invocation is not used; 
    #     # continue even if this invocation fails
    #     print("Order status ({:d}) sent to the error microservice:".format(
    #         code), order_result)


    # Inform the error microservice


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0" ,port=5308, debug=True)


    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
