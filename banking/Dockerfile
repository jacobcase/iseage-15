
FROM ubuntu:14.04

RUN apt-get update && apt-get -y install python3-pip libyaml-dev

RUN pip3 install flask tornado pyyaml flask-sqlalchemy pymysql 

COPY banking /tmp/incres

RUN cd /tmp/incres && python3 setup.py install 

RUN rm -r /tmp/incres

VOLUME /config

CMD ["python3", "-m", "banking", "-c", "/config/config.yml"]
