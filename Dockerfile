# TODO: See if 3.11 works
FROM python:3.10.4-alpine

# cchardet, and multiple other dependencies require GCC to build.
RUN apk add --no-cache build-base libffi-dev

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
ENV GEVENT=true

COPY . .

EXPOSE 5000

CMD [ "python", "docker.py" ]