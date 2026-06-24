FROM node:8.17.0-buster

ENV WORKDIR="/usr/src/app"

WORKDIR $WORKDIR

RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list \
    && sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list \
    && sed -i '/buster-updates/d' /etc/apt/sources.list \
    && apt-get update -o Acquire::Check-Valid-Until=false \
    && apt-get install -y --no-install-recommends git \
    && git config --global url."https://github.com/".insteadOf git://github.com/ \
    && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json $WORKDIR/
RUN npm install && npm cache clean --force

COPY . $WORKDIR

EXPOSE 4200

CMD ["npm", "run", "start"]
