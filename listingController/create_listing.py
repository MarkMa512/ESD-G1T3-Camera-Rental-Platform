from flask import Flask, request, jsonify
from flask_cors import CORS
import json

import os
import sys

from invokes import invoke_http

import os
import sys
import json

import pika
import amqp_setup
import requests

app = Flask(__name__)
CORS(app)

"""
For localhost testing:
"""
email_url = "http://localhost:5301/listedEmail"
# image_url = "http://localhost:5302/image"
sms_url = "http://localhost:5306/listedSMS"
listing_url = "http://localhost:5304/listing"
user_phone_url = "http://localhost:5303/userphone/"

"""
for docker deployment
"""
# email_url = os.environ.get('EMAIL_URL')
# sms_url = os.environ.get('SMS_URL')
# list_url = os.environ.get('LIST_URL')


@app.route("/create_listing", methods=['POST'])
def create_listing():
    # 1. validate the JSON sent over by the client
    if request.is_json:
        try:
            listing = request.get_json()  # listing is of type dict
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
    """
    1. Invoke the listing microservice to create the listing
    """
    print('\n ---Invoking listing microservice---')
    create_listing_result = invoke_http(
        url=listing_url, method='POST', json=listing)
    # create_listing_result is a type of dictionary

    # Check the create listing result; if a failure, send it to the error microservice.
    code = create_listing_result["code"]
    create_listing_message = json.dumps(create_listing_result)

    # if there is an error, send it to the error microservice
    if code not in range(200, 300):
        print('an error has occurred')
        print(create_listing_message)

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="listing.error",
                                         body=create_listing_message, properties=pika.BasicProperties(delivery_mode=2))
        # make create_listing_message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails
        print("\n list Creation status ({:d}) published to the RabbitMQ Exchange:".format(
            code), create_listing_result)

        # # Return error
        return {
            "code": 500,
            "data": {"listing creation result result": create_listing_result},
            "create_listing_message": "listing creation failure sent for error handling."
        }

    # Since the "Activity Log" binds to the queue using '#' => any routing_key would be matched
    # and a create_listing_message sent to “Error” queue can be received by “Activity Log” too.

    else:
        print("\n\n----list creation successful!----")
        # record the activity log anyway
        print('\n\n-----Invoking activity_log microservice-----')
        print(
            '\n\n-----Publishing the (listing info) create_listing_message with routing_key=listing.info-----')

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="listing.info",
                                         body=create_listing_message, properties=pika.BasicProperties(delivery_mode=2))

    print("\nlisting information published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails

    """
    2. Invoke user microservice to get user phone number
    """
    print('\n\n-----Invoking user microservice to get phone number-----')
    listing_description = listing['listing_description']
    print("listing_description is: " + listing_description)
    owner_id = listing['owner_id']
    print("owner_id is: " + owner_id)
    get_owner_phone_number_result = invoke_http(
        url=user_phone_url+owner_id, method='GET')
    # get_owner_phone_number_result is of type dict
    owner_phone_number = str(get_owner_phone_number_result['data'])
    print("owner_phone_number : " + owner_phone_number)
    data_pack = {
        "listing_description": listing_description,
        "email": owner_id,
        "phone": owner_phone_number}

    """
    3. Invoke email microservice to send email to owner

    """
    print('\n\n-----Invoking email microservice-----')

    email_sending_result = invoke_http(
        email_url, method="POST", json=data_pack)
    email_sending_message = json.dumps(email_sending_result)
    print("email_sending_result: ", email_sending_result, '\n')

    # Check the email sent result;
    # if a failure, send it to the error microservice.
    code = email_sending_result["code"]
    if code not in range(200, 300):
        #     # Inform the error microservice
        print('\n\n-----Publishing the (email error) email_sending_message with routing_key=email.error-----')
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.error",
                                         body=email_sending_message, properties=pika.BasicProperties(delivery_mode=2))

        print("\n email send status ({:d}) published to the RabbitMQ Exchange:".format(
            code), email_sending_result)
    else:
        print('\n\n-----Invoking activity_log microservice-----')
        print(
            '\n\n-----Publishing the (email info) email_sending_message with routing_key=email.info-----')

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.info",
                                         body=email_sending_message, properties=pika.BasicProperties(delivery_mode=2))

    """
    4. Invoke SMS microservice to send email to owner
    """
    print('\n\n-----Invoking sms microservice-----')

    sms_sending_result = invoke_http(
        sms_url, method="POST", json=data_pack)
    print("sms_sending_result:", sms_sending_result, '\n')
    sms_sending_message = json.dumps(sms_sending_result)
    # Check the sms_sending_result;
    # if a failure, send it to the error microservice.
    code = sms_sending_result["code"]
    if code not in range(200, 300):
        #     # Inform the error microservice
        print('\n\n-----Publishing the (sms error) sms_sending_message with routing_key=email.error-----')

    #     # invoke_http(error_URL, method="POST", json=shipping_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="sms.error",
                                         body=sms_sending_message, properties=pika.BasicProperties(delivery_mode=2))

        print("\n sms status ({:d}) published to the RabbitMQ Exchange:".format(
            code), sms_sending_result)
    else:
        print('\n\n-----Invoking activity_log microservice-----')
        print('\n\n-----Publishing the (email info) sms_sending_message with routing_key=sms.info-----')

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="sms.info",
                                         body=sms_sending_message, properties=pika.BasicProperties(delivery_mode=2))

    # 7. Return create_listing_result, email_sent_result, sms_sending_result
    return {
        "code": 201,
        "data": {
            "create_listing_result": create_listing_result,
            "email_sending_result": email_sending_result,
            "sms_sending_result": sms_sending_result
        }
    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(port=5309, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
