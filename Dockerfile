FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY Pipfile* /app/

WORKDIR /app

RUN set -ex; \
  pip install pipenv; \
  pipenv install --system --deploy;

COPY ./src /app