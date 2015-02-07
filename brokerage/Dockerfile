
FROM ubuntu:14.04

ENV http_proxy="http://199.100.16.100:3128" https_proxy="http://199.100.16.100:3128" ftp_proxy="http://199.100.16.100:3128"

RUN apt-get update && apt-get -y install python3-pip libyaml-dev

RUN pip3 install flask tornado pyyaml flask-sqlalchemy pymysql 

COPY brokerage /tmp/broker

RUN cd /tmp/broker && python3 setup.py install 

RUN rm -r /tmp/broker

VOLUME /config

CMD ["python3", "-m", "brokerage", "-c", "/config/config.yml"]
