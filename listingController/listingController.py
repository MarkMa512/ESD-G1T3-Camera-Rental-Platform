from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import sys
import json

import pika
# import amqp_setup

import requests
from complex.invokes import invoke_http

app = Flask(__name__)
CORS(app)

"""
For localhost testing:
"""
email_url = "http://localhost:5301/email"
image_url = "http://localhost:5302/image"
sms_url = "http://localhost:5306/sms"
listing_url = "http://localhost:5304/"

"""
for docker deployment
"""
# email_url = os.environ.get('EMAIL_URL')
# image_url = os.environ.get('IMAGE_URL')
# user_url = os.environ.get('USER_URL')
# sms_url = os.environ.get('SMS_URL')
# list_url = os.environ.get('LIST_URL')


@app.route("/createListing", methods=['POST'])
def create_listing():
    # 1. validate the JSON sent over by the client
    if request.is_json:
        try:
            listing = request.get_json()
            print("\n recieved listing creation request: ", listing)

            result = process_create_listing(listing)
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


def process_create_listing(listing):
    print('\n ---Invoking listing microservice---')
    create_listing_result = invoke_http(listing_url, 'POST', listing)

    # Check the create listing result; if a failure, send it to the error microservice.
    code = create_listing_result["code"]
    message = json.dumps(create_listing_result)

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
            code), create_listing_result)

        # Return error
        return {
            "code": 500,
            "data": {"listing creation result result": create_listing_result},
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

    # 5. Invoke email microservice to send email to owner
    # Invoke the shipping record microservice
    print('\n\n-----Invoking email microservice-----')

    email_send_result = invoke_http(
        email_url, method="POST", json=create_listing_result['data'])
    print("shipping_result:", email_send_result, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = email_send_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (email error) message with routing_key=email.error-----')

        # invoke_http(error_URL, method="POST", json=shipping_result)
        message = json.dumps(email_send_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.error",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))

        print("\nShipping status ({:d}) published to the RabbitMQ Exchange:".format(
            code), email_send_result)

        # 7. Return error
        return {
            "code": 400,
            "data": {
                "listring_creation_result": create_listing_result,
                "email_sent_result": email_send_result
            },
            "message": ""
        }

    # 5. Invoke sms microservice to send email to owner
    # Invoke the shipping record microservice
    print('\n\n-----Invoking sms microservice-----')

    sms_sending_result = invoke_http(
        sms_url, method="POST", json=create_listing_result['data'])
    print("shipping_result:", sms_sending_result, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = sms_sending_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (email error) message with routing_key=email.error-----')

        # invoke_http(error_URL, method="POST", json=shipping_result)
        message = json.dumps(email_send_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.error",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))

        print("\nShipping status ({:d}) published to the RabbitMQ Exchange:".format(
            code), email_send_result)

        # 7. Return error
        return {
            "code": 400,
            "data": {
                "listring_creation_result": create_listing_result,
                "email_sent_result": sms_sending_result
            },
            "message": ""
        }

    # 7. Return created order, shipping record
    return {
        "code": 201,
        "data": {
            "create_listing_result": create_listing_result,
            "email_sent_result": sms_sending_result
        }
    }
