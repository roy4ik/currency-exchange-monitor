FROM mongo:latest

COPY mongo_password.txt /run/secrets/mongo_password.txt
COPY mongo_user.txt /run/secrets/mongo_user.txt
COPY shared/tests /service/db/tests

EXPOSE 27017