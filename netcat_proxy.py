# Skrypt działa jak 'netcat', tworząc tunel przez serwer proxy HTTP do docelowego hosta i portu.
# Umożliwia interaktywną, dwukierunkową komunikację z serwerem docelowym.

import threading
import socks
import argparse

parser = argparse.ArgumentParser(description="Utworz tunel HTTP connect z hostem")
parser.add_argument('target_host', help="Adres hosta")
parser.add_argument('target_port', type=int, help="Port hosta")
parser.add_argument('proxy_host',  help="Adres serwera proxy")
parser.add_argument('proxy_port', type=int, help="Port serwera proxy")
parser.add_argument('--timeout', type=int, default=10, help="Czas oczekiwania na polaczenie (w sekundach)")
args = parser.parse_args()

proxy_host = args.proxy_host
proxy_port = args.proxy_port
target_host = args.target_host
target_port = args.target_port

s = socks.socksocket()
s.set_proxy(socks.HTTP, proxy_host, proxy_port)
s.settimeout(10)
s.connect((target_host, target_port))

def receive_from_server(sock):
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            print("Serwer: " + data.decode(), end='')
    except:
        pass

def send_to_server(sock):
    try:
        while True:
            line = input()
            sock.sendall(line.encode() + b'\n')
    except KeyboardInterrupt:
        print("Zakonczono")
    finally:
        sock.close()

T1 = threading.Thread(target=receive_from_server, args=(s,), daemon=True)
T2 = threading.Thread(target=send_to_server, args=(s,), daemon=True)
T1.start()
T2.start()
T1.join()
T2.join()