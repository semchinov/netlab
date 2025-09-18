# src/pop3_client.py
from __future__ import annotations

import argparse
import socket
import ssl
import io
from typing import Tuple

CRLF = b"\r\n"
DEFAULT_SEPARATOR = "----- MESSAGE 1 START -----"

# Дефолты под локальный мок-сервер
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 1100
DEFAULT_USER = "test"
DEFAULT_PASSWORD = "secret"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simple POP3 client via raw sockets")
    p.add_argument("--host", default=DEFAULT_HOST, help="POP3 server host (default: 127.0.0.1)")
    p.add_argument("--port", type=int, default=DEFAULT_PORT, help="POP3 server port (110 plain, 995 TLS, default: 1100)")
    p.add_argument("--user", default=DEFAULT_USER, help="Username (default: test)")
    p.add_argument("--password", default=DEFAULT_PASSWORD, help="Password (default: secret)")
    p.add_argument("--timeout", type=float, default=10.0, help="Socket timeout (seconds)")
    p.add_argument("--ssl", action="store_true", help="Use SSL/TLS (wrap socket). For explicit TLS on port 995")
    p.add_argument("--separator", type=str, default=DEFAULT_SEPARATOR, help="Separator before message body printout")
    return p.parse_args()


def make_connection(host: str, port: int, timeout: float, use_ssl: bool) -> Tuple[socket.socket, io.BufferedReader]:
    s = socket.create_connection((host, port), timeout=timeout)
    if use_ssl:
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)
    # file-like обёртка для удобного readline()
    f = s.makefile("rb")
    return s, f


def read_line(f) -> bytes:
    """Read one line (bytes, includes CRLF)."""
    return f.readline()


def send_cmd(sock: socket.socket, f, cmd: str) -> bytes:
    """Send command (without CRLF) and return the single-line server response (bytes)."""
    sock.sendall(cmd.encode("ascii") + CRLF)
    return read_line(f)


def read_multiline(f) -> bytes:
    """
    Read POP3 multi-line response terminated by a single line with b'.\\r\\n'.
    Handle dot-stuffing (lines starting with b'..' -> b'.').
    """
    parts = []
    while True:
        line = read_line(f)
        if not line:
            break
        if line == b".\r\n":
            break
        if line.startswith(b".."):
            line = line[1:]
        parts.append(line)
    return b"".join(parts)


def decode_bytes(b: bytes) -> str:
    try:
        return b.decode("utf-8")
    except Exception:
        return b.decode("iso-8859-1", errors="replace")


def run_pop3_session(host: str, port: int, user: str, password: str, timeout: float, use_ssl: bool, separator: str):
    sock, f = make_connection(host, port, timeout, use_ssl)

    try:
        # Banner
        banner = read_line(f)
        print("S:", banner.decode("utf-8", errors="replace").rstrip())

        # USER
        resp = send_cmd(sock, f, f"USER {user}")
        print("S:", resp.decode("utf-8", errors="replace").rstrip())

        # PASS
        resp = send_cmd(sock, f, f"PASS {password}")
        print("S:", resp.decode("utf-8", errors="replace").rstrip())

        # STAT
        resp = send_cmd(sock, f, "STAT")
        stat_line = resp.decode("utf-8", errors="replace").rstrip()
        print("S:", stat_line)
        parts = stat_line.split()
        count = int(parts[1]) if len(parts) >= 2 and parts[0].upper().startswith("+OK") else 0

        # LIST (multi-line)
        resp = send_cmd(sock, f, "LIST")
        first = resp.decode("utf-8", errors="replace").rstrip()
        print("S:", first)
        if first.upper().startswith("+OK"):
            listing = read_multiline(f)
            print(decode_bytes(listing).rstrip())
        else:
            print("LIST failed or returned error.")

        if count >= 1:
            # RETR 1
            resp = send_cmd(sock, f, "RETR 1")
            first = resp.decode("utf-8", errors="replace").rstrip()
            print("S:", first)
            if first.upper().startswith("+OK"):
                message_bytes = read_multiline(f)
                print(separator)
                print(decode_bytes(message_bytes).rstrip())
            else:
                print("RETR 1 failed or returned error.")
        else:
            print("No messages to RETR.")

        # QUIT
        resp = send_cmd(sock, f, "QUIT")
        print("S:", resp.decode("utf-8", errors="replace").rstrip())

    finally:
        try: f.close()
        except Exception: pass
        try: sock.close()
        except Exception: pass


def main():
    args = parse_args()
    run_pop3_session(
        args.host,
        args.port,
        args.user,
        args.password,
        args.timeout,
        args.ssl,
        args.separator,
    )


if __name__ == "__main__":
    main()