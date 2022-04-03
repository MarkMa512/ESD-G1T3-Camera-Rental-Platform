from flask import Flask, request, jsonify
from flask_cors import CORS
import json

import os
import sys

import requests
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


@app.route("/createListing", methods=['POST'])
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
    print('\n ---Invoking listing microservice---')
    create_listing_result = invoke_http(listing_url, 'POST', listing)
    # create_listing_result is a type of dictionary

    # Check the create listing result; if a failure, send it to the error microservice.
    code = create_listing_result["code"]
    message = json.dumps(create_listing_result)

    if code not in range(200, 300):
        print('an error has occurred')
        print(message)

        # # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="listing.error",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))
        # # make message persistent within the matching queues until it is received by some receiver
        # # (the matching queues have to exist and be durable and bound to the exchange)

        # # - reply from the invocation is not used;
        # # continue even if this invocation fails
        print("\n list Creation status ({:d}) published to the RabbitMQ Exchange:".format(
            code), create_listing_result)

        # # Return error
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
        print("list creation successful!")
        # 4. Record new order
        # record the activity log anyway
        print('\n\n-----Invoking activity_log microservice-----')
        print(
            '\n\n-----Publishing the (listing info) message with routing_key=listing.info-----')

        # invoke_http(activity_log_URL, method="POST", json=order_result)

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="listing.info",
                                         body=message)

    # print("\nlisting ifnromation published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails

    """
    invoke user microservice to get user phone number
    """
    print('\n\n-----Invoking user microservice to get phone number-----')
    listing_description = listing['listing_description']
    print("listing_description is: " + listing_description)

    owner_id = listing['owner_id']
    print("owner_id is: " + owner_id)

    get_owner_phone_number_result = invoke_http(user_phone_url+owner_id, 'GET')
    # get_owner_phone_number_result is of type dict
    owner_phone_number = str(get_owner_phone_number_result['data'])
    print("owner_phone_number : " + owner_phone_number)

    data_pack = {
        "listing_id": listing_description,
        "email": owner_id,
        "phone": owner_phone_number}

    print("The data_pack is: " + data_pack)

    """
    5. Invoke email microservice to send email to owner
    
    """
    # print('\n\n-----Invoking email microservice-----')

    email_sending_result = invoke_http(
        email_url, method="POST", json=data_pack)
    print("email_sending_result: ", email_sending_result, '\n')

    # Check the email sent result;
    # if a failure, send it to the error microservice.
    # code = email_send_result["code"]
    # if code not in range(200, 300):
    #     # Inform the error microservice
    #     print('\n\n-----Publishing the (email error) message with routing_key=email.error-----')

    #     # invoke_http(error_URL, method="POST", json=shipping_result)
    #     message = json.dumps(email_send_result)
    #     amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.error",
    #                                      body=message, properties=pika.BasicProperties(delivery_mode=2))

    #     print("\nShipping status ({:d}) published to the RabbitMQ Exchange:".format(
    #         code), email_send_result)

    #     # 7. Return error
    #     return {
    #         "code": 400,
    #         "data": {
    #             "listring_creation_result": create_listing_result,
    #             "email_sent_result": email_send_result
    #         },
    #         "message": ""
    #     }

    # 5. Invoke sms microservice to send email to owner
    # print('\n\n-----Invoking sms microservice-----')

    sms_sending_result = invoke_http(
        sms_url, method="POST", json=data_pack)
    print("sms_sending_result:", sms_sending_result, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    # code = sms_sending_result["code"]
    # if code not in range(200, 300):
    #     # Inform the error microservice
    #     print('\n\n-----Publishing the (email error) message with routing_key=email.error-----')

    #     # invoke_http(error_URL, method="POST", json=shipping_result)
    #     message = json.dumps(sms_sending_result)
    #     amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.error",
    #                                      body=message, properties=pika.BasicProperties(delivery_mode=2))

    #     print("\nShipping status ({:d}) published to the RabbitMQ Exchange:".format(
    #         code), email_send_result)

    #     # 7. Return error
    #     return {
    #         "code": 400,
    #         "data": {
    #             "listring_creation_result": create_listing_result,
    #             "email_sent_result": sms_sending_result
    #         },
    #         "message": ""
    #     }

    # 7. Return creatling_listing, shipping record
    return {
        "code": 201,
        "data": {
            "create_listing_result": create_listing_result,
            # "email_sent_result": sms_sending_result
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
