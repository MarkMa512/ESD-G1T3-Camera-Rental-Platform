FROM python:3-slim
WORKDIR /usr/src/app
COPY accept_requirements.txt ./
RUN python -m pip install --no-cache-dir -r accept_requirements.txt
COPY ./accept_rental.py ./invokes.py ./amqp_setup.py ./
CMD [ "python", "./accept_rental.py" ]