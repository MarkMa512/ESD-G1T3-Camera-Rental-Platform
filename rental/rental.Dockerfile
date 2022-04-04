FROM python:3-slim
WORKDIR /usr/src/app
COPY rental_requirements.txt ./
RUN python -m pip install --no-cache-dir -r rental_requirements.txt
COPY ./rental.py .
CMD [ "python", "./rental.py" ]