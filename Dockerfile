FROM python:3.7-alpine

RUN pip install pipenv
#RUN apk add build-base openssl-dev libffi-dev libxml2-dev libxslt-dev

COPY Pipfile /logclouseau/Pipfile
COPY Pipfile.lock /logclouseau/Pipfile.lock

WORKDIR /logclouseau

RUN pipenv install

COPY . /logclouseau

CMD ["pipenv", "run", "python", "logclouseau.py", "--config", "/logclouseau/logclouseau.toml"]
