FROM --platform=linux/amd64 python:3.6

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

RUN pipenv --python 3.6 \
    && python - <<'PY' > /tmp/requirements.txt
import json

with open('Pipfile.lock') as lock_file:
    lock_data = json.load(lock_file)

for package_name, package_data in sorted(lock_data['default'].items()):
    version = package_data.get('version', '')
    markers = package_data.get('markers')
    requirement = f'{package_name}{version}'
    if markers:
        requirement = f'{requirement}; {markers}'
    print(requirement)
PY
RUN pipenv run pip install -r /tmp/requirements.txt

COPY . $WORKDIR

COPY docker/mongodb_config.py $WORKDIR/air_pollution/config/mongodb_config.py

CMD ["pipenv", "run", "./www"]
