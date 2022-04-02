from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

rental_URL = "http://localhost:5305/rental"
listing_URL = "http://localhost:5304/listing"
email_url = "http://localhost:5301/requestedEmail"



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

#     # 4. Record new order
#     print('\n\n-----Invoking activity_log microservice-----')
#     invoke_http(activity_log_URL, method="POST", json=order_result)
#     print("\nOrder sent to activity log.\n")
#     # - reply from the invocation is not used;
#     # continue even if this invocation fails
#     # record the activity log anyway

#     # Check the order result; if a failure, send it to the error microservice.
#     code = order_result["code"]
#     if code not in range(200, 300):
#         print('\n\n-----Invoking error microservice as order fails-----')
#         invoke_http(error_URL, method="POST", json=order_result)
#         # - reply from the invocation is not used; 
#         # continue even if this invocation fails
#         print("Order status ({:d}) sent to the error microservice:".format(
#             code), order_result)


#     # Inform the error microservice

#     # 7. Return error
#     return {
#             "code": 500,
#             "data": {"order_result": order_result},
#             "message": "Order creation failure sent for error handling."
#         }


#     # 5. Send new order to shipping
#     # Invoke the shipping record microservice
#     print('\n\n-----Invoking shipping_record microservice-----')
#     shipping_result = invoke_http(
#         shipping_record_URL, method="POST", json=order_result['data'])
#     print("shipping_result:", shipping_result, '\n')


#     # Check the shipping result;
#     # if a failure, send it to the error microservice.
#     code = shipping_result["code"]
#     if code not in range(200, 300):


#     # Inform the error microservice
#         print('\n\n-----Invoking error microservice as shipping fails-----')
#         invoke_http(error_URL, method="POST", json=shipping_result)
#         print("Shipping status ({:d}) sent to the error microservice:".format(code), shipping_result)


#     # 7. Return error
#     return {
#             "code": 400,
#             "data": {
#                 "order_result": order_result,
#                 "shipping_result": shipping_result
#             },
#             "message": "Simulated shipping record error sent for error handling."
#         }
    """
    invoke method to get user phone number
    """
    list_id = rental['listing_id']
    print("list_id is: " + list_id)
    owner_id = rental['renter_id']
    print("owner_id" + owner_id)
    # owner_phone_number = invoke_http(user_url+owner_id, 'POST', listing)
    owner_phone_number = "+6593835210"
    data_pack = {"listing_id": list_id,
                 "email": owner_id, "phone": owner_phone_number}
    print(data_pack)

    """
    5. Invoke email microservice to send email to owner
    """
    # print('\n\n-----Invoking email microservice-----')

    email_sending_result = invoke_http(
        email_url, method="POST", json=data_pack)
    print("email_sending_result:", email_sending_result, '\n')

    sms_sending_result = invoke_http(
    sms_url, method="POST", json=data_pack)
    print("sms_sending_result:", sms_sending_result, '\n')

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

    # sms_sending_result = invoke_http(
    #     sms_url, method="POST", json=data_pack)
    # print("sms_sending_result:", sms_sending_result, '\n')



    # 7. Return created order, shipping record
    return {"code": 201,
        "data": {
            "rental_result": rental_result,
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
