FROM python:3.6

ENV WORKDIR="/usr/src/app"
ENV SHELL="/bin/bash"

RUN apt-get update \
    && apt-get install -y cron \
    && mkdir -p $WORKDIR \
    && pip install --user pipenv

ENV PATH="/root/.local/bin:$PATH"
WORKDIR $WORKDIR

COPY Pipfile $WORKDIR/Pipfile
COPY Pipfile.lock $WORKDIR/Pipfile.lock

RUN pipenv install --skip-lock

COPY . $WORKDIR

COPY docker/mongodb_config.py $WORKDIR/air_pollution/config/mongodb_config.py

CMD ["pipenv", "run", "./www"]
