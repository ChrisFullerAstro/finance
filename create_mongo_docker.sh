docker run -p 5001:27017 --name mongo -d mongo
docker run -d --link mongo:mongo -p 8081:8081 --name mongo-express mongo-express
