FROM python:3-slim
WORKDIR /usr/src/app
COPY placerental_requirements.txt ./
RUN python -m pip install --no-cache-dir -r placerental_requirements.txt
COPY ./place_rental.py .
CMD [ "python", "./place_rental.py" ]