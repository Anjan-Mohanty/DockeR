FROM python:3.8.5
RUN apt-get -y update && apt-get -y install apt-utils build-essential libxml2-dev zlib1g-dev python-dev python-pip pkg-config libffi-dev libcairo-dev
COPY . /app
EXPOSE 5300
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD ["uwsgi","app.ini"]