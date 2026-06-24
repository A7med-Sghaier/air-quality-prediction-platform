FROM node:8.17.0-buster

ENV WORKDIR="/usr/src/app"

WORKDIR $WORKDIR

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && git config --global url."https://github.com/".insteadOf git://github.com/ \
    && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json $WORKDIR/
RUN npm install && npm cache clean --force

COPY . $WORKDIR

EXPOSE 4200

CMD ["npm", "run", "start"]
