#!/usr/bin/env python3

import json
import socket
import struct
import os


HOST = "::"
PORT = 5000
client = None


# -------- EV3-Funktionen --------

def handle_list_dir(message):
    path = message.get("path")

    if not path:
        return {"type": "error", "message": "No path provided"}

    try:
        entries = []
        for name in os.listdir(path):
            entry_path = os.path.join(path, name)
            if os.path.isdir(entry_path):
                entries.append({"name": name, "type": "directory"})
            elif os.path.isfile(entry_path):
                entries.append({"name": name, "type": "file", "executable": os.access(entry_path, os.X_OK), "size": os.path.getsize(entry_path)})
        return {"type": "dir_listing", "path": path, "entries": entries}

    except OSError as e:
        return {"type": "error", "message": str(e)}


# -------- Verbindung --------

def receive_exactly(sock, size):
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Verbindung geschlossen")
        data.extend(chunk)
    return bytes(data)


def receive_message(sock):
    header = receive_exactly(sock, 4)
    length = struct.unpack("!I", header)[0]
    payload = receive_exactly(sock, length)
    return json.loads(payload.decode("utf-8"))


def send_message(sock, message):
    payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def handle_message(message):
    message_type = message.get("type")

    if message_type == "list_dir":
        return handle_list_dir(message)


def main():
    global client
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print("Agent laeuft auf Port " + str(PORT))
    while True:
        client = None
        try:
            print("Warte auf PC-Verbindung...")
            client, address = server.accept()
            print("Verbindung von " + str(address))
            while True:
                message = receive_message(client)
                print("Empfangen:", message)
                response = handle_message(message)
                if response is not None:
                    send_message(client, response)
        except ConnectionError:
            print("PC getrennt")
        except Exception as e:
            print("Fehler: " + str(e))
        finally:
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass


if __name__ == "__main__":
    main()