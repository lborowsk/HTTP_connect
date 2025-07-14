# Skrypt manualnie tworzy tunel HTTP CONNECT do docelowego hosta przez serwer proxy.
# Umożliwia interaktywną komunikację z serwerem docelowym lub pobranie pliku z serwera.

import threading
import socket
import argparse

parser = argparse.ArgumentParser(description="Utworz tunel HTTP connect z hostem")
parser.add_argument('target_host', help="Adres hosta docelowego")
parser.add_argument('target_port', type=int, help="Port hosta docelowego")
parser.add_argument('proxy_host',  help="Adres serwera proxy")
parser.add_argument('proxy_port', type=int, help="Port serwera proxy")
parser.add_argument('--timeout', type=int, default=10, help="Czas oczekiwania na polaczenie (w sekundach)")
parser.add_argument('--file', type=str, help="Nazwa pliku do zapisu odpowiedzi")
args = parser.parse_args()

proxy_host = args.proxy_host
proxy_port = args.proxy_port
target_host = args.target_host
target_port = args.target_port
timeout = args.timeout
filename = args.file

connect_http = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}:{target_port}\r\n\r\n"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(timeout)
s.connect((proxy_host, proxy_port))
s.send(connect_http.encode())

try:
    data = s.recv(4096)
    if data:
        response = data.decode()
        arr = response.split(' ')
        if arr[1] == "200":
            print("Nawiazano polaczenie")
        else:
            print("Nie nawiazano polaczenia")
            raise ConnectionError
except:
    raise ConnectionError("Nie nawiazano polaczenia")

def receive_from_server(sock):
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            print("Serwer: " + data.decode(), end='')
    except:
        pass

def file_from_server(sock):
    with open(filename, 'ab') as f:
        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                f.write(data)
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

if filename:
    T1 = threading.Thread(target=file_from_server, args=(s,), daemon=True)
else:
    T1 = threading.Thread(target=receive_from_server, args=(s,), daemon=True)

T2 = threading.Thread(target=send_to_server, args=(s,), daemon=True)
T1.start()
T2.start()
T1.join()
T2.join()