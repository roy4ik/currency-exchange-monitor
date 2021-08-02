FROM python:3.9

RUN mkdir /service

COPY protobufs/ /service/protobufs/
COPY settings /service/alerts_monitor/settings
COPY alerts_monitor/ /service/alerts_monitor/
COPY shared/tests /service/alerts_monitor/tests

WORKDIR /service/alerts_monitor/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/exchangerates.proto

EXPOSE 50051

ENTRYPOINT [ "python", "/service/alerts_monitor/alerts_monitor.py" ]