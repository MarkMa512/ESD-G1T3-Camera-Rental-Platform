FROM python:3-slim
WORKDIR /usr/src/app
COPY place_rental_requirements.txt ./
RUN python -m pip install --no-cache-dir -r place_rental_requirements.txt   
COPY ./place_rental.py ./invokes.py ./amqp_setup.py ./
CMD [ "python", "./place_rental.py" ]