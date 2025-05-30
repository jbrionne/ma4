#FROM python:3.11-slim-bookworm
FROM python:3.11-slim-bookworm@sha256:44f3da9d702a293500f4e23619db3bbd2558e5931a0b27e45792e54b1ea41933

ARG USER_ID
ARG GROUP_ID

USER root

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup --gid $GROUP_ID techuser
RUN adduser --uid $USER_ID --gid $GROUP_ID --shell /bin/sh techuser
WORKDIR /home/techuser

RUN mkdir /home/techuser/work
RUN chown techuser:techuser /home/techuser/work
VOLUME /home/techuser/work

ENV PATH="/home/techuser/.local/bin:$PATH" 


RUN apt-get update && apt install -y curl
RUN printf "deb http://deb.debian.org/debian/ bookworm-proposed-updates main" > /etc/apt/sources.list.d/proposedupdates.list
RUN apt-get update && apt-get install -fy chromium
RUN apt-get update && apt-get install -fy jq

ADD docker-entrypoint.sh docker-entrypoint.sh
RUN chmod 755 docker-entrypoint.sh && chown techuser:techuser docker-entrypoint.sh

WORKDIR /home/techuser/work

USER techuser

ENTRYPOINT ["../docker-entrypoint.sh"]