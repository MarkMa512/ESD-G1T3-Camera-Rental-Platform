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

app = Flask(__name__)
CORS(app)

rental_URL = "http://localhost:5305/rental"
listing_URL = "http://localhost:5304/listing"
email_url = "http://localhost:5301/requestedEmail"
sms_url = "http://localhost:5306/requestedSMS"




@app.route("/place_rental", methods=['POST'])
def place_rental():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            rental = request.get_json()
            print("\nReceived an rental request in JSON:", rental)

            # do the actual work
            # 1. Send order info {cart items}
            result = processPlaceRental(rental)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processPlaceRental(rental):
    # 2. Send the order info {cart items}
    # Invoke the order microservice
    print("\n-----  Invoking Order Micro Service ------- ")
    rental_result = invoke_http(rental_URL, method = "POST", json = rental)
    print('rental_result:', rental_result)

    code = rental_result["code"]
    message = json.dumps(rental_result)

    if code not in range(200, 300):
        print('an error has occurred')
        print(rental_result)

        # # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="rental.error",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))
        # # make message persistent within the matching queues until it is received by some receiver
        # # (the matching queues have to exist and be durable and bound to the exchange)

        # # - reply from the invocation is not used;
        # # continue even if this invocation fails
        print("\n Rental Creation status ({:d}) published to the RabbitMQ Exchange:".format(
            code), rental_result)

        return {
            "code": 500,
            "data": {"listing creation result result": rental_result},
            "message": "listing creation failure sent for error handling."
        }

    else:
        print("Rental creation successful")
        print(" invoking activity.py")
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="rental.info",
                                         body=message, properties=pika.BasicProperties(delivery_mode=2))


    """
    2. Invoke user microservice to get user phone number
    """
    print('\n\n-----Invoking user microservice to get phone number-----')
    list_id = rental['listing_id']
    print("list_id is: " + list_id)
    owner_id = rental['owner_id'] #put as renter_id if you want to test -> setItems as ur email in add-rental
    print("owner_id" + owner_id)
    owner_phone_number = "+6592385972"
    print("owner_phone_number : " + owner_phone_number)
    data_pack = {
        "listing_description": list_id,
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
            "rental_result": rental_result,
            "email_sending_result": email_sending_result,
            "sms_sending_result": sms_sending_result
        }
    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(port=5307, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
