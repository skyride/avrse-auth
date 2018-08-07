FROM python:2.7-alpine

WORKDIR /app

RUN apk update && \
    apk add postgresql-libs && \
    apk add --virtual .builds-deps gcc g++ musl-dev postgresql-dev ca-certificates wget bzip2-dev
RUN pip install psycopg2
RUN pip install --global-option=build_ext --global-option="-D__USE_UNIX98" zeroc-ice==3.7.0

COPY requirements.txt /app
RUN pip install -r requirements.txt