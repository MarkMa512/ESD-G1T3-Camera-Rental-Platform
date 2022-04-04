FROM python:3-slim
WORKDIR /usr/src/app
COPY sms_requirements.txt ./
RUN python -m pip install --no-cache-dir -r sms_requirements.txt
COPY ./smsNotification.py .
CMD [ "python", "./smsNotification.py"]