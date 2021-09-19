docker build -t edgebot:latest .
docker tag edgebot:latest cbevard1/edgebot:latest
docker push cbevard1/edgebot:latest