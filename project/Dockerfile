# pull official base image
FROM python:3.11-slim-buster

# set working directory
WORKDIR /usr/src/app

# add user
RUN adduser myuser --disabled-login --disabled-password --home /var/lib/myuser --shell /bin/false

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean

# install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

# install ffmpeg
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ffmpeg

# add app
COPY . .
RUN chmod +x entrypoint.sh

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chown -R myuser:myuser /usr/src/app
USER myuser
