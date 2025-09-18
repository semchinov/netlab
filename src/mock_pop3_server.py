# mock_pop3_server.py
import argparse
import socket
import threading

CRLF = "\r\n"

SAMPLE_MAIL = """From: alice@example.com
To: you@example.com
Subject: Test message

Hello!
This is a test message.
."""

def handle_client(conn, addr):
    with conn:
        conn.sendall(("+OK Mock POP3 server ready" + CRLF).encode())
        buf = b""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buf += data
            if b"\r\n" not in buf:
                continue
            line, buf = buf.split(b"\r\n", 1)
            cmd = line.decode().strip()
            if cmd.upper().startswith("USER"):
                conn.sendall(("+OK user accepted" + CRLF).encode())
            elif cmd.upper().startswith("PASS"):
                conn.sendall(("+OK pass accepted" + CRLF).encode())
            elif cmd.upper().startswith("STAT"):
                # 1 message, size in bytes
                size = len(SAMPLE_MAIL.encode())
                conn.sendall((f"+OK 1 {size}" + CRLF).encode())
            elif cmd.upper().startswith("LIST"):
                conn.sendall(("+OK scan listing follows" + CRLF).encode())
                conn.sendall((f"1 {len(SAMPLE_MAIL.encode())}" + CRLF).encode())
                conn.sendall(("." + CRLF).encode())
            elif cmd.upper().startswith("RETR 1"):
                conn.sendall(("+OK 1 message follows" + CRLF).encode())
                # dot-stuffing: if any line starts with '.', prefix another '.'
                for line in SAMPLE_MAIL.splitlines():
                    if line.startswith("."):
                        conn.sendall(("." + line + CRLF).encode())
                    else:
                        conn.sendall((line + CRLF).encode())
                conn.sendall(("." + CRLF).encode())
            elif cmd.upper().startswith("QUIT"):
                conn.sendall(("+OK goodbye" + CRLF).encode())
                break
            else:
                conn.sendall(("+ERR unknown command" + CRLF).encode())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=1100)
    args = p.parse_args()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((args.host, args.port))
    srv.listen(5)
    print(f"Mock POP3 listening on {args.host}:{args.port}")
    try:
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    finally:
        srv.close()

if __name__ == "__main__":
    main()
