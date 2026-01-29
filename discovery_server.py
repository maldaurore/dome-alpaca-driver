import socket
import json
import threading

DISCOVERY_PORT = 32227
DISCOVERY_STRING = b"alpacadiscovery1"
ALPACA_PORT = 5000

def discovery_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", DISCOVERY_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        if data.strip().lower() == DISCOVERY_STRING:
            response = {
                "AlpacaPort": ALPACA_PORT
            }
            sock.sendto(json.dumps(response).encode("utf-8"), addr)

def start_discovery():
    thread = threading.Thread(target=discovery_server, daemon=True)
    thread.start()
