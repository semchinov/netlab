
## POP3s

```bash
IFACE=$(route -n get pop.gmail.com | awk '/interface:/{print $2}')
```

```bash
sudo tcpdump -i "$IFACE" -s 0 -w src/artifacts/pop3s/traces/pop3s-client.pcap \
  'tcp port 995 and host pop.gmail.com'
```

```bash
python -m src.pop3_client \
  --host pop.gmail.com --port 995 --ssl \
  --user "mike.network.cu@gmail.com" --password "APP_PASSWORD" \
  --timeout 15 \
  --separator "----- MESSAGE 1 START -----" \
  | tee src/artifacts/pop3s/session.log

```

