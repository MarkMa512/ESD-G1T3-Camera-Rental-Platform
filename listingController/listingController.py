from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import sys
import json

import pika
import amqp_setup

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

# URL used to retrieve User information
user_url = 'http://user-management:5111/user'
# URL used to retieve listing information
listing_url = "http://localhost:5100/"
image_url = "http://localhost:5000/"  # URL used to retrieve images
sms_url = "http://localhost:5200/"  # URL used to send SMS
email_url = "http://localhost:5200/"  # URL used to send email


@app.route("/createListing", methods=['POST'])
def create_listing():
    # 1. validate the JSON sent over by the client
    if request.is_json:
        try:
            listing = request.get_json()
            print("\n recieved listing creation request: ", listing)

            result = processCreateListing(listing)
            return jsonify(result), result['code']

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + \
                fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "createListing.py internal error: " + ex_str
            }), 500

    # if reached here, it is not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processCreateListing(listing):
    print('\n ---Invoking listing microservice---')
    createListingResult = invoke_http(listing_url, 'POST', listing)

    # Check the order result; if a failure, send it to the error microservice.
    code = createListingResult["code"]
    message = json.dumps(createListingResult)

    if code not in range(200, 300):
        print('\n\n ---Invoking error microservice---')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="listing.error",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))
        # make message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails
        print("\n list Creation status ({:d}) published to the RabbitMQ Exchange:".format(
            code), createListingResult)

        # 7. Return error
        return {
            "code": 500,
            "data": {"listing creation result result": createListingResult},
            "message": "listing creation failure sent for error handling."
        }

    # Notice that we are publishing to "Activity Log" only when there is no error in order creation.
    # In http version, we first invoked "Activity Log" and then checked for error.
    # Since the "Activity Log" binds to the queue using '#' => any routing_key would be matched
    # and a message sent to “Error” queue can be received by “Activity Log” too.

    else:
        # 4. Record new order
        # record the activity log anyway
        #print('\n\n-----Invoking activity_log microservice-----')
        print(
            '\n\n-----Publishing the (listing info) message with routing_key=listing.info-----')

        # invoke_http(activity_log_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="listing.info",
                                         body=message)

    print("\nlisting ifnromation published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails

    # 5. Send new order to shipping
    # Invoke the shipping record microservice
    print('\n\n-----Invoking email microservice-----')

    emailSendingResult = invoke_http(
        email_url, method="POST", json=createListingResult['data'])
    print("shipping_result:", emailSendingResult, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = emailSendingResult["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (email error) message with routing_key=email.error-----')

        # invoke_http(error_URL, method="POST", json=shipping_result)
        message = json.dumps(emailSendingResult)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.error",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))

        print("\nShipping status ({:d}) published to the RabbitMQ Exchange:".format(
            code), emailSendingResult)

        # 7. Return error
        return {
            "code": 400,
            "data": {
                "listring_creation_result": createListingResult,
                "email_sent_result": emailSendingResult
            },
            "message": ""
        }

    # 7. Return created order, shipping record
    return {
        "code": 201,
        "data": {
            "create_listing_result": createListingResult,
            "email_sent_result": emailSendingResult
        }
    }
