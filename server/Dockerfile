FROM --platform=linux/amd64 python:3.6

ENV WORKDIR="/usr/src/app"
ENV SHELL="/bin/bash"
ENV PYTHONPATH="/usr/src/app"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && mkdir -p $WORKDIR \
    && rm -rf /var/lib/apt/lists/*

WORKDIR $WORKDIR

RUN pip install --no-cache-dir \
        falcon==1.4.1 \
        falcon-cors==1.1.7 \
        waitress==1.1.0 \
        pymongo==3.7.0 \
        python-dateutil==2.7.3 \
    && python - <<'PY'
import bson
import dateutil.parser
import falcon
import falcon_cors
import pymongo
import waitress
print('Core API dependencies are installed')
PY

COPY . $WORKDIR

COPY docker/mongodb_config.py $WORKDIR/air_pollution/config/mongodb_config.py

RUN python - <<'PY'
from air_pollution.api.air_app import pandasApi
print('Backend API imports successfully')
PY

CMD ["./www"]
