FROM python:3.9.6-slim-buster

ENV PROJECT_DIR=/app
ENV PYTHONPATH /app

RUN apt update && apt -y upgrade
RUN apt install -y postgresql-client

WORKDIR $PROJECT_DIR

COPY ./requirements.txt $PROJECT_DIR/requirements.txt
RUN pip install -r $PROJECT_DIR/requirements.txt

COPY ./ /app/
RUN chmod +x /app/run_dev_server.sh

CMD ["/app/run_server.sh"]
