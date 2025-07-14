# Skrypt łączy się z podanym hostem i portem przez serwer proxy HTTP.
# Może obsługiwać zarówno połączenia HTTP, jak i HTTPS, a następnie wyświetla odpowiedź serwera.

import argparse
import socks
import socket
import ssl

parser = argparse.ArgumentParser(description="Utworz tunel HTTP connect z hostem")
parser.add_argument('host', help="Adres hosta")
parser.add_argument('port', type=int, help="Port hosta")
parser.add_argument('proxy_host',  help="Adres serwera proxy")
parser.add_argument('proxy_port', type=int, help="Port serwera proxy")
parser.add_argument('--https', action="store_true", help="Uzycie https", default=False)
parser.add_argument('--timeout', type=int, default=10, help="Czas oczekiwania na polaczenie (w sekundach)")
args = parser.parse_args()

proxy_host = args.proxy_host
proxy_port = args.proxy_port
timeout = args.timeout
host = args.host
port = args.port
use_https = args.https

s = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(timeout)
s.set_proxy(socks.HTTP, proxy_host, proxy_port, rdns=True)
s.connect((host, port))

if use_https:
    context = ssl.create_default_context()
    s = context.wrap_socket(s, server_hostname=host)
    request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
else:
    request = f"GET http://{host}/ HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

s.sendall(request.encode())

response = b""
while True:
    data = s.recv(4096)
    if not data:
        break
    response += data

print(response.decode(errors="replace"))
s.close()