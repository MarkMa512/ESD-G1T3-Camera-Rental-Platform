FROM python:3-slim
WORKDIR /usr/src/app
COPY create_listing_requirements.txt ./
RUN python -m pip install --no-cache-dir -r create_listing_requirements.txt
COPY ./create_listing.py .
CMD [ "python", "./create_listing.py" ]