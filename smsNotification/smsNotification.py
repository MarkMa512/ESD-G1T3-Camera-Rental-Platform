from twilio.rest import Client
import keys


def send_sms(to_number, message):
    client = Client(keys.account_sid, keys.auth_token)
    client.messages.create(
        to=to_number,
        from_=keys.twilio_number,
        body=message)
    return "success"

# client = Client(keys.account_sid, keys.auth_token)

# message = client.messages.create(
#     body="This is a new message from Camera Rental Platform!",
#     from_=keys.twilio_number,
#     to=keys.my_phone_number
# )
