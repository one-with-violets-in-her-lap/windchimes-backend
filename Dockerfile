FROM ghcr.io/astral-sh/uv:alpine

RUN apk update
RUN apk upgrade
RUN apk add --no-cache ffmpeg

WORKDIR /app

ADD . /app

RUN uv sync --locked

ENTRYPOINT "./start.sh"
