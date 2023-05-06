# head-detect-annotator

# Native docker
- `docker build` 時に環境引数PASSWORDを設定
- `docker create (run)` 時に `data` ディレクトリをマウント

```
docker build -t head-detect-annotator . --build-arg PASSWORD=password
docker run -d -p 8080:5000 -v /path/to/data:/var/www/data head-detect-annotator
```

# docker-compose
```
cp sample.docker-compose.yml docker-compose.yml
# Rewite password, port and volumes
docker-compose up -d --build
```
