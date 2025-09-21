
## HTTP-HTTPS

request_1
```bash
python -m src.http_client "https://example.org/" --timeout 15 --separator "===== BODY ====="
```


request_2_browser
`https://example.org/`

request_3_curl
```bash
curl --http1.1 https://example.org/ -o /tmp/example.html
```
