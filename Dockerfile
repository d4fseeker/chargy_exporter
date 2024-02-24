# pull official base image
FROM python:3.9-alpine

# Environment variables
ENV PYTHONDONTWRITEBYTECODE 1   # Disable .pyc files
ENV PYTHONUNBUFFERED 1          # Disable stdout buffering

# Install requirements
RUN apk add build-base

# Install app dependencies
RUN pip install --no-cache-dir --upgrade pip
COPY ./requirements.txt /tmp
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

# Copy app
COPY ./src /app

#Set workdir
WORKDIR /app

#PROD: Compile Python .pyc
RUN python -m compileall .

#Command
USER 1001:0
CMD [ "python" ,  "exporter.py" ]
