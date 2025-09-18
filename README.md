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
