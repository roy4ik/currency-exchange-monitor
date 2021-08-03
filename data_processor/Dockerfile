FROM python:3.9

RUN mkdir /service

COPY protobufs/ /service/protobufs/
COPY data_processor/ /service/data_processor/
COPY settings /service/data_processor/settings
COPY config /service/data_processor/config
COPY shared/ /service/data_processor/

COPY mongo_password.txt /run/secrets/mongo_password.txt
COPY mongo_user.txt /run/secrets/mongo_user.txt

WORKDIR /service/data_processor/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt


EXPOSE 50051

ENTRYPOINT [ "python", "/service/data_processor/data_processor.py"]