FROM python:3-slim
WORKDIR /usr/src/app
COPY rental_requirements.txt ./
RUN python -m pip install --no-cache-dir -r rental_requirements.txt
COPY ./accept_rental.py .
CMD [ "python", "./accept_rental.py" ]