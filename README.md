# netlab

## Network Emulation Lab

### Project structure

```markdown
netlab/
  README.md
  requirements.txt
  src/
    http_client.py
    pop3_client.py
    mock_pop3_server.py
```

### HTTP-client

```bash
python -m src.http_client --help
```

```bash
python -m src.http_client http://example.com
```

```bash
python -m src.http_client "https://example.org/" \
    --timeout 20 \
    --max-redirects 2 \
    --separator "===== PAGE BODY ====="
```


### POP3-client

```bash
python -m src.pop3_client --help
```

#### Mock POP3 server
```bash
python -m src.mock_pop3_server
```

```bash
python -m src.pop3_client
```

```bash
python -m src.pop3_client \
  --host 127.0.0.1 \
  --port 1100 \
  --user test \
  --password secret \
  --timeout 15 \
  --separator "===== MESSAGE BODY ====="
```
