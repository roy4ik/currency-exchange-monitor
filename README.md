# currency-exchange-monitor

###This is part of an assignment to create a microservice infrastructure that provides alerts on exchange rates if the rate increases beyond a set threshold in relation to the base currency.

###Services: 
* A data processor that catches new exchange rates via an external API and feeds it to a database
* A database service (MongoDB)
* An alerts monitor that watches changes in rates and sends it to a message queue if the rate change exceeds threshold
* A kafka message queue
* An alerts handler that receives the messages from the message queue and sends it to a webhook via an HTTP request

###Tech-Stack:
* Python3.9
* MongoDB
* KafkaMQ
* Docker
 
###Prerequisites:
* To run this make sure you have docker installed (https://www.docker.com/products/docker-desktop)

* Create a .txt file for your mongo password and update the paths in the config, this should only contain one line: 
`<password>`

* Create a .txt file for your mongo user and  update the paths in the config this should only contain one line: 
`<user>`

### How to Run: 
`docker-compose up` in terminal

