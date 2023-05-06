FROM python:3.11

ARG PASSWORD="password"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www

COPY . /var/www
WORKDIR /var/www

RUN python3 -m pip install -U pip
RUN python3 -m pip install -r /var/www/requirements.txt

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
