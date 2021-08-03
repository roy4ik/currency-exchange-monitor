FROM python:3.9

RUN mkdir /service

COPY settings /service/alerts_handler/settings
COPY config /service/alerts_handler/config
COPY alerts_handler/ /service/alerts_handler/
COPY shared/tests /service/alerts_handler/tests

COPY mongo_password.txt /run/secrets/mongo_password.txt
COPY mongo_user.txt /run/secrets/mongo_user.txt

WORKDIR /service/alerts_handler/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt


EXPOSE 50051

ENTRYPOINT [ "python", "/service/alerts_monitor/alerts_handler.py" ]