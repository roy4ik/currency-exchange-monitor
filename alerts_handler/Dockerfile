FROM python:3.9

RUN mkdir /service

COPY settings /service/alerts_handler/settings
COPY config /service/alerts_handler/config
COPY alerts_handler/ /service/alerts_handler/
COPY shared/mngrs /service/alerts_handler/mngrs

WORKDIR /service/alerts_handler/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
ENV PYTHONUNBUFFERED=1


EXPOSE 50051

ENTRYPOINT ["python", "/service/alerts_handler/alerts_handler.py" ]