FROM python:3-slim
WORKDIR /usr/src/app
COPY image_requirements.txt ./
RUN python -m pip install --no-cache-dir -r image_requirements.txt
COPY ./image.py ./db.py ./models.py ./
CMD [ "python", "./image.py" ]
