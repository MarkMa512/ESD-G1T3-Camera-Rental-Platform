FROM python:3-slim
WORKDIR /usr/src/app
COPY listing_requirements.txt ./
RUN python -m pip install --no-cache-dir -r listing_requirements.txt
COPY ./listing.py .
CMD [ "python", "./listing.py" ]
