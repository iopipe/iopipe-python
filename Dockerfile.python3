FROM lambci/lambda:build-python3.6

RUN pip install -U setuptools

RUN mkdir -p /var/lib/iopipe

WORKDIR /var/lib/iopipe

COPY . /var/lib/iopipe

RUN python setup.py test
