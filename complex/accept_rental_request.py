from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

rental_URL = "http://localhost:5000/rental"
listing_URL = "http://localhost:5001/listing"
user_url = "http://localhost:5002/user"         # check port num
# activity_log_URL = "http://localhost:5003/activity_log"
# error_URL = "http://localhost:5004/error"


@app.route("/accept_request", methods=['POST'])
def accept_request():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            request = request.get_json()
            print("\nReceived a rental request in JSON:", request)
            # do the actual work
            # Send rental request info {cart items}
            result = processAcceptRequest(request)
            
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "accept_rental_request.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processAcceptRequest(request):
    
    # 1. Invoke the rental microservice
    print('\n-----Invoking rental microservice-----')
    request_result = invoke_http(rental_URL, method='POST', json=rental)
    # print('rental_result:', rental_result)
    
    # Check the rental result; if a failure, send it to the error microservice.
    code = rental_result["code"]
    if code not in range(200, 300):

        # Inform the error microservice
        print('\n\n-----Invoking error microservice as request fails-----')
        invoke_http(error_URL, method="POST", json=rental_result)
        # - reply from the invocation is not used; 
        # continue even if this invocation fails
        print("Rental request status ({:d}) sent to the error microservice:".format(
        code), rental_result)

        # 7. Return error
        return {
                "code": 500,
                "data": {"rental_result": rental_result},
                "message": "Rental details retrival failure sent for error handling."
            }
    
    # 2. Invoke listing microservice
    print('\n-----Invoking listing microservice-----')
    listing_result = invoke_http(listing_URL, method='POST', json=listing)
    # print('listing_result:', listing_result)
    
    # Check the listing result; if a failure, send it to the error microservice.
    code = listing_result["code"]
    if code not in range(200, 300):

        # Inform the error microservice
        print('\n\n-----Invoking error microservice as request fails-----')
        invoke_http(error_URL, method="POST", json=listing_result)
        # - reply from the invocation is not used; 
        # continue even if this invocation fails
        print("Listing details status ({:d}) sent to the error microservice:".format(
        code), listing_result)

        # 7. Return error
        return {
                "code": 500,
                "data": {"listing_result": listing_result},
                "message": "Listing details retrival failure sent for error handling."
            }


    # 3. Invoke user microservice








    # Send new order to shipping
    # Invoke the shipping record microservice
    print('\n\n-----Invoking shipping_record microservice-----')
    shipping_result = invoke_http(shipping_record_URL, method="POST", json=order_result['data'])
    print("shipping_result:", shipping_result, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = shipping_result["code"]
    if code not in range(200, 300):

        # Inform the error microservice
        print('\n\n-----Invoking error microservice as shipping fails-----')
        invoke_http(error_URL, method="POST", json=shipping_result)
        print("Shipping status ({:d}) sent to the error microservice:".format(
        code), shipping_result)

        # 7. Return error
        return {
                "code": 400,
                "data": {
                    "order_result": order_result,
                    "shipping_result": shipping_result
                },
                "message": "Simulated shipping record error sent for error handling."
            }

    # 7. Return created order, shipping record
    return {"code": 201,
        "data": {
            "order_result": order_result,
            "shipping_result": shipping_result
        }
    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5100, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
