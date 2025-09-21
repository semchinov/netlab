# TLS ClientHello extensions

| Extension | request_1.pcapng | request_2_browser.pcapng | request_3_curl.pcapng |
|---|---|---|---|
| application_layer_protocol_negotiation | — | len=14 | len=11 |
| compress_certificate | — | len=3 | — |
| ec_point_formats | len=4 | len=2 | len=2 |
| encrypted_client_hello | — | len=250 | — |
| encrypt_then_mac | len=0 | — | — |
| extended_master_secret | len=0 | len=0 | — |
| key_share | len=38 x25519 | len=1263 X25519MLKEM768, x25519 | len=38 x25519 |
| padding | len=217 | — | — |
| psk_key_exchange_modes | len=2 | len=2 | — |
| renegotiation_info | len=1 | len=1 | — |
| Reserved (GREASE) | — | len=0; len=1 | — |
| server_name | len=16 name=example.org | len=16 name=example.org | len=16 name=example.org |
| session_ticket | len=0 | len=0 | — |
| signature_algorithms | len=48 | len=18 | len=24 |
| signed_certificate_timestamp | — | len=0 | — |
| status_request | — | len=5 | — |
| supported_groups | len=22 | len=12 | len=10 |
| supported_versions | len=5 TLS 1.3, TLS 1.2 | len=7 TLS 1.3, TLS 1.2 | len=9 TLS 1.3, TLS 1.2, TLS 1.1, TLS 1.0 |
| Unknown type 17613 | — | len=5 | — |