# pull official base image
FROM python:3.9.5-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apk update
RUN apk add postgresql-dev gcc g++ python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
RUN addgroup -S junkfood && adduser -S junkfood -G junkfood
RUN chown junkfood /usr/src/app
COPY --chown=junkfood . /usr/src/app/ 

USER junkfood