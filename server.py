import concurrent.futures
import json
import os
import socket
import struct
import threading
from typing import Any, Dict


HOST = "0.0.0.0"
PORT = 5000
MAX_WORKERS = max(4, (os.cpu_count() or 1) * 2)


def recv_exact(sock: socket.socket, nbytes: int) -> bytes:
    data = bytearray()
    while len(data) < nbytes:
        chunk = sock.recv(nbytes - len(data))
        if not chunk:
            raise ConnectionError("Conexión cerrada por el cliente")
        data.extend(chunk)
    return bytes(data)


def recv_json(sock: socket.socket) -> Dict[str, Any]:
    header = recv_exact(sock, 4)
    (length,) = struct.unpack("!I", header)
    if length > 10_000_000:
        raise ValueError("Mensaje demasiado grande")
    payload = recv_exact(sock, length)
    return json.loads(payload.decode("utf-8"))


def send_json(sock: socket.socket, obj: Dict[str, Any]) -> None:
    raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    header = struct.pack("!I", len(raw))
    sock.sendall(header + raw)


def perform_task(task: Dict[str, Any]) -> Dict[str, Any]:
    op = task.get("op")
    data = task.get("data")
    task_id = task.get("id")

    if op == "echo":
        result = data
    elif op == "upper":
        result = str(data).upper()
    elif op == "sum":
        if not isinstance(data, list):
            raise ValueError("'data' debe ser una lista de números")
        result = sum(float(x) for x in data)
    else:
        raise ValueError(f"Operación no soportada: {op}")

    return {"id": task_id, "ok": True, "result": result}


def handle_client(conn: socket.socket, addr, executor: concurrent.futures.ThreadPoolExecutor):
    try:
        while True:
            try:
                task = recv_json(conn)
            except ConnectionError:
                break

            future = executor.submit(perform_task, task)
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001
                result = {"id": task.get("id"), "ok": False, "error": str(exc)}

            send_json(conn, result)
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass


def serve(host: str = HOST, port: int = PORT, max_workers: int = MAX_WORKERS) -> None:
    print(f"Servidor escuchando en {host}:{port} con {max_workers} workers...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="worker")

        try:
            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=handle_client, args=(conn, addr, executor), daemon=True)
                t.start()
        except KeyboardInterrupt:
            print("Apagando servidor...")
        finally:
            executor.shutdown(wait=True)


if __name__ == "__main__":
    serve()


