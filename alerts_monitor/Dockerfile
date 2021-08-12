FROM python:3.9

RUN mkdir /service

COPY settings /service/alerts_monitor/settings
COPY config /service/alerts_monitor/config
COPY alerts_monitor/ /service/alerts_monitor/
COPY shared/ /service/alerts_monitor/

COPY mongo_password.txt /run/secrets/mongo_password.txt
COPY mongo_user.txt /run/secrets/mongo_user.txt

WORKDIR /service/alerts_monitor/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
ENV PYTHONUNBUFFERED=1

EXPOSE 50051

ENTRYPOINT [ "python", "/service/alerts_monitor/alerts_monitor.py" ]