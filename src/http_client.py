# src/http_client.py
from __future__ import annotations

import argparse
import socket
import ssl
from urllib.parse import urlparse, urljoin
import re

CRLF = b"\r\n"
HEADER_BODY_SEP = b"\r\n\r\n"
DEFAULT_UA = "netlab-http-client/0.1"
DEFAULT_SEPARATOR = "----- BODY START -----"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simple HTTP client via raw sockets")
    p.add_argument("url", nargs="?", help="Page URL, e.g. http://example.com/ or https://example.com/")
    p.add_argument("--timeout", type=float, default=10.0, help="Socket timeout (seconds)")
    p.add_argument("--max-redirects", type=int, default=5, help="Follow up to N redirects")
    p.add_argument("--separator", type=str, default=DEFAULT_SEPARATOR, help="Header/body separator line")
    return p.parse_args()


def make_connection(parsed, timeout: float) -> socket.socket:
    """
    Returns a connected socket (wrapped with SSL if https).
    """
    scheme = parsed.scheme.lower()
    host = parsed.hostname
    port = parsed.port or (443 if scheme == "https" else 80)

    s = socket.create_connection((host, port), timeout=timeout)
    if scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)
    return s


def build_request(parsed) -> bytes:
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query

    # HTTP/1.1 + Connection: close (чтобы сервер закрыл сокет после ответа)
    lines = [
        f"GET {path} HTTP/1.1",
        f"Host: {parsed.hostname}",
        f"User-Agent: {DEFAULT_UA}",
        "Accept: */*",
        "Connection: close",
        "",  # пустая строка перед телом
        "",
    ]
    return CRLF.join(line.encode("ascii") for line in lines)


def recv_all(sock: socket.socket) -> bytes:
    chunks = []
    while True:
        data = sock.recv(65536)
        if not data:
            break
        chunks.append(data)
    return b"".join(chunks)


def split_headers_body(raw: bytes) -> tuple[str, bytes]:
    """
    Returns (headers_text, body_bytes)
    """
    idx = raw.find(HEADER_BODY_SEP)
    if idx == -1:
        # Нет разделителя — считаем всё заголовками (редкий случай)
        return raw.decode("iso-8859-1", "replace"), b""
    head = raw[:idx].decode("iso-8859-1", "replace")
    body = raw[idx + len(HEADER_BODY_SEP):]
    return head, body


def parse_status_code(headers_text: str) -> int:
    # Первая строка формата: HTTP/1.1 200 OK
    first_line = headers_text.splitlines()[0] if headers_text else ""
    m = re.match(r"HTTP/\d\.\d\s+(\d{3})", first_line)
    return int(m.group(1)) if m else 0


def get_header(headers_text: str, name: str) -> str | None:
    name_lower = name.lower()
    for line in headers_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            if k.strip().lower() == name_lower:
                return v.strip()
    return None


def decode_chunked(body: bytes) -> bytes:
    """
    Very small, robust chunked decoder.
    """
    i = 0
    out = bytearray()
    while True:
        # read chunk size line
        j = body.find(CRLF, i)
        if j == -1:
            break
        size_line = body[i:j].decode("ascii", "replace").split(";", 1)[0].strip()
        try:
            size = int(size_line, 16)
        except ValueError:
            break
        i = j + 2
        if size == 0:
            # skip trailing headers after last chunk
            # ends with CRLF CRLF typically; we can ignore rest
            break
        out += body[i:i + size]
        i += size
        # skip trailing CRLF after chunk data
        if body[i:i + 2] == CRLF:
            i += 2
    return bytes(out)


def body_text_from_bytes(body: bytes, headers_text: str) -> str:
    # Try charset from Content-Type
    ct = get_header(headers_text, "Content-Type") or ""
    m = re.search(r"charset=([^\s;]+)", ct, flags=re.IGNORECASE)
    encoding = (m.group(1) if m else "utf-8").strip("\"'").lower()
    try:
        return body.decode(encoding, errors="replace")
    except LookupError:
        return body.decode("utf-8", errors="replace")


def fetch_once(url: str, timeout: float) -> tuple[str, bytes]:
    """
    Returns (headers_text, body_bytes) for a single HTTP request.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http/https schemes are supported")

    with make_connection(parsed, timeout) as s:
        req = build_request(parsed)
        s.sendall(req)
        raw = recv_all(s)

    headers_text, body = split_headers_body(raw)

    # chunked?
    te = get_header(headers_text, "Transfer-Encoding") or ""
    if "chunked" in te.lower():
        body = decode_chunked(body)

    return headers_text, body


def fetch_follow_redirects(url: str, timeout: float, max_redirects: int) -> tuple[str, bytes, str]:
    current = url
    for _ in range(max_redirects + 1):
        headers_text, body = fetch_once(current, timeout)
        code = parse_status_code(headers_text)
        if code in (301, 302, 303, 307, 308):
            loc = get_header(headers_text, "Location")
            if not loc:
                break
            current = urljoin(current, loc)
            continue
        return headers_text, body, current
    # Если вышли из цикла из-за редиректов — вернём последнее
    return fetch_once(current, timeout) + (current,)


def main():
    args = parse_args()
    url = args.url or "https://example.org/"
    headers_text, body, final_url = fetch_follow_redirects(
        url, args.timeout, args.max_redirects
    )

    # Печатаем заголовки как есть:
    print(headers_text)

    # Разделитель:
    print(args.separator)

    # Печатаем тело (стараемся декодировать как текст web-страницы):
    print(body_text_from_bytes(body, headers_text))


if __name__ == "__main__":
    main()
