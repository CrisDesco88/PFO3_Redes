## Arquitectura distribuida con sockets (demo)

Este repositorio contiene:

- Diagrama de arquitectura distribuida (`docs/diagrama.md`) con clientes, balanceador (NGINX/HAProxy), servidores workers con pool de hilos, RabbitMQ para comunicación entre servidores y almacenamiento distribuido (PostgreSQL y S3).
- Implementación de referencia en Python de:
  - Servidor TCP que recibe tareas por socket y las ejecuta en un pool de hilos (`server.py`).
  - Cliente que envía tareas y recibe resultados (`client.py`).

La implementación de sockets es local y minimalista para pruebas. En producción, el balanceo (NGINX/HAProxy) enrutaría hacia varios `server.py` desplegados. RabbitMQ se usa entre servidores para coordinación/fan-out (no requerido para correr esta demo básica).

### Requisitos

- Python 3.9+

Instalar dependencias (opcionales para futuras extensiones):

```bash
pip install -r requirements.txt
```

> Para la demo básica de sockets, no se requieren paquetes externos.

### Ejecutar el servidor

```bash
python server.py
```

El servidor escucha por defecto en `0.0.0.0:5000`.

### Probar con el cliente

```bash
# echo
python client.py 127.0.0.1 5000 echo '"hola"'

# upper
python client.py 127.0.0.1 5000 upper '"hola"'

# sum
python client.py 127.0.0.1 5000 sum '[1,2,3,4]'
```

Salida esperada (ejemplo):

```json
{
  "id": "<uuid>",
  "ok": true,
  "result": 10.0
}
```

### Protocolo

- Mensajes enmarcados: `uint32` big-endian (longitud) + bytes JSON UTF-8.
- Petición: `{ "id": string, "op": "echo|upper|sum", "data": any }`.
- Respuesta OK: `{ "id": string, "ok": true, "result": any }`.
- Respuesta ERROR: `{ "id": string, "ok": false, "error": string }`.

### Escalamiento y componentes (según diagrama)

- Balanceo con NGINX/HAProxy hacia múltiples instancias del servidor.
- RabbitMQ para distribuir trabajos entre servidores cuando una tarea excede un nodo o requiere reintentos.
- PostgreSQL para estado transaccional; S3/MinIO para blobs/artefactos.

### Notas de producción

- Añadir TLS/mtls para sockets o usar TLS terminado en el balanceador.
- Healthchecks en servidores y límites de concurrencia por cola.
- Observabilidad: métricas, trazas y logs estructurados.


