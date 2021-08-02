FROM python:3.9

RUN mkdir /service

COPY protobufs/ /service/protobufs/
COPY settings /service/data_processor/settings
COPY data_processor/ /service/data_processor/
COPY shared/tests /service/data_processor/tests

WORKDIR /service/data_processor/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/exchangerates.proto

EXPOSE 50051

ENTRYPOINT [ "python", "/service/data_processor/data_processor.py"]