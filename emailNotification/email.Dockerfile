FROM python:3-slim
WORKDIR /usr/src/app
COPY email_requirements.txt ./
RUN python -m pip install --no-cache-dir -r email_requirements.txt
COPY ./emailNofication.py .
CMD [ "python", "./emailNofication.py" ]