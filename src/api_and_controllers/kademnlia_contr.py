import argparse
import logging
import asyncio
import threading
import socket
import subprocess

# Inside script1.py
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network import start_network, connect_node, set, get
from kademlia.network import Server

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)


container_ip = subprocess.check_output(
    "hostname -i", shell=True).decode("utf-8").strip()
print(container_ip)
stop_thread = False


def bc_server():
    host = '0.0.0.0'
    port = 8888

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    server_socket.setblocking(0)

    while not stop_thread:
        try:
            data, addr = server_socket.recvfrom(1024)
            if addr[0] != container_ip:
                print(f"Received: {data}, from: {addr}")
                server_socket.sendto(b"OK...hello", addr)
        except Exception as e:
            print(e)


def bc_client():
    host = '255.255.255.255'
    port = 8888
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    client_socket.settimeout(10.0)

    try:
        msg = "Where are you at?"
        print("Waiting for response of other servers")
        client_socket.sendto(msg.encode('utf-8'), (host, port))
        data, addr = client_socket.recvfrom(1024)
        print(f"Received: {data}, from: {addr}")
        return addr[0]
    except:
        log.info("No server responded, proceeding to start network")
        print("No server responded, proceeding to start network")
        return None


def parse_arguments():
    parser = argparse.ArgumentParser()

    # Optional arguments
    parser.add_argument("-o", "--operation", help="desired data operation to perform (get or set)",
                        type=str, default=None, choices=['get', 'set'])
    parser.add_argument(
        "-k", "--key", help="key of the data", type=str, default=None)
    parser.add_argument(
        "-v", "--value", help="value of the data", type=str, default=None)
    return parser.parse_args()


def main(loop):
    global stop_thread
    args = parse_arguments()

    ip = bc_client()
    port = 8468

    server = Server(ip)

    if ip == None:
        start_network(server, loop)
    elif args.operation == 'set':
        if args.key and args.value:
            asyncio.run(set(server, ip, port, args))
            stop_thread = True
            return
    elif args.operation == 'get':
        if args.key:
            result = asyncio.run(get(server, ip, port, args))
            stop_thread = True
            print(result)
            return result
    else:
        connect_node(server, ip, port, loop)


if __name__ == "__main__":
    # Create a new loop
    new_loop = asyncio.new_event_loop()

    # Run the loop in a new thread
    t = threading.Thread(target=main, args=(new_loop,))
    t.start()

    # Do something with the loop
    try:
        asyncio.run_coroutine_threadsafe(bc_server(), new_loop)
    except Exception as e:
            print(e)

    t.join()
