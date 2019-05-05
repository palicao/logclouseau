FROM python:3.7-alpine

RUN pip install pip-tools
#RUN apk add build-base openssl-dev libffi-dev libxml2-dev libxslt-dev

COPY requirements.txt /logclouseau/requirements.txt

WORKDIR /logclouseau

RUN pip-sync

COPY src /logclouseau

CMD ["python", "logclouseau.py", "--config", "/logclouseau/logclouseau.toml"]
