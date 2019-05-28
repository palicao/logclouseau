FROM python:3.7-alpine

RUN pip install pip-tools
RUN apk update && \
    apk upgrade && \
    apk add --no-cache git gcc musl-dev libffi-dev

COPY requirements.txt /logclouseau/requirements.txt

WORKDIR /logclouseau

RUN pip-sync

COPY . /logclouseau
COPY logclouseau.toml.dist /root/.logclouseau/logclouseau.toml

RUN python setup.py install

CMD ["logclouseau"]
