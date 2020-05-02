FROM python:3.7
RUN /usr/local/bin/python -m pip install --upgrade pip

ADD . /opt
WORKDIR /opt

RUN pip install -r ./conf/requirements-dev.txt