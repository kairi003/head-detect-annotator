# head-detect-annotator

- `docker build` 時に環境引数PASSWORDを設定
- `docker create (run)` 時に `data` ディレクトリをマウント

```
docker build -t head-detect-annotator . --build-arg PASSWORD=password
docker run -p 8080:5000 -v /path/to/data:/var/www/data head-detect-annotator
```