FROM python:3.9.6-slim-buster

ENV PROJECT_DIR=/app
ENV PYTHONPATH /app

RUN apt update && apt -y upgrade

WORKDIR $PROJECT_DIR

COPY ./requirements.txt $PROJECT_DIR/requirements.txt
RUN pip install -r $PROJECT_DIR/requirements.txt

COPY ./ /app/
RUN chmod +x /app/run_dev_server.sh

CMD ["/app/run_dev_server.sh"]
