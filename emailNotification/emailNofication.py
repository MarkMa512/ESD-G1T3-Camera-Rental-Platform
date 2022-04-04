import smtplib
from email.message import EmailMessage

from keys import *
import email


def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = keys.esd_email
    msg['from'] = user
    password = keys.app_password

    # server parameter
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()


# def listed


# if __name__ == '__main__':
#     email_alert("ESD Notification Test", "ESD Test",
#                 keys.esd_email)


# 2FA for gmail account is required
