import json
import socket
import struct
import sys
import uuid
from typing import Any, Dict


def send_json(sock: socket.socket, obj: Dict[str, Any]) -> None:
    raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    header = struct.pack("!I", len(raw))
    sock.sendall(header + raw)


def recv_exact(sock: socket.socket, nbytes: int) -> bytes:
    data = bytearray()
    while len(data) < nbytes:
        chunk = sock.recv(nbytes - len(data))
        if not chunk:
            raise ConnectionError("Conexión cerrada por el servidor")
        data.extend(chunk)
    return bytes(data)


def recv_json(sock: socket.socket) -> Dict[str, Any]:
    header = recv_exact(sock, 4)
    (length,) = struct.unpack("!I", header)
    payload = recv_exact(sock, length)
    return json.loads(payload.decode("utf-8"))


def main():
    if len(sys.argv) < 4:
        print("Uso: python client.py <host> <port> <op> [data_json]")
        print("Ejemplos:")
        print("  python client.py 127.0.0.1 5000 echo '""hola""'")
        print("  python client.py 127.0.0.1 5000 upper '""hola""'")
        print("  python client.py 127.0.0.1 5000 sum '[1,2,3]'")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    op = sys.argv[3]
    data: Any
    if len(sys.argv) >= 5:
        raw = sys.argv[4]
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = raw
    else:
        data = None

    task = {"id": str(uuid.uuid4()), "op": op, "data": data}

    with socket.create_connection((host, port)) as sock:
        send_json(sock, task)
        result = recv_json(sock)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


