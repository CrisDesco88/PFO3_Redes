## Diagrama de arquitectura distribuida

```mermaid
flowchart LR
    subgraph Clientes
        A1[App Móvil]
        A2[App Web]
    end

    A1 --> LB
    A2 --> LB

    subgraph Balanceador
        LB[NGINX / HAProxy]
    end

    LB --> S1
    LB --> S2
    LB --> S3

    subgraph Servidores_Workers
        direction TB
        S1[Servidor Worker 1\n(Socket Server)]
        S2[Servidor Worker 2\n(Socket Server)]
        S3[Servidor Worker 3\n(Socket Server)]

        S1 --- P1[Pool de hilos]
        S2 --- P2[Pool de hilos]
        S3 --- P3[Pool de hilos]
    end

    subgraph Mensajería
        MQ[RabbitMQ\n(Cola de mensajes entre servidores)]
    end

    S1 <--> MQ
    S2 <--> MQ
    S3 <--> MQ

    subgraph Almacenamiento
        DB[(PostgreSQL)]
        S3S[(S3 / MinIO)]
    end

    S1 <--> DB
    S2 <--> DB
    S3 <--> DB
    S1 <--> S3S
    S2 <--> S3S
    S3 <--> S3S

    classDef comp fill:#eef,stroke:#88a,stroke-width:1px;
    classDef queue fill:#efe,stroke:#484,stroke-width:1px;
    classDef store fill:#fee,stroke:#a88,stroke-width:1px;
    class A1,A2,LB,S1,S2,S3,P1,P2,P3 comp;
    class MQ queue;
    class DB,S3S store;
```

Notas:
- RabbitMQ se utiliza para coordinación y distribución de trabajos entre servidores cuando una tarea requiere fan-out/fan-in o reintentos.
- El balanceador enruta conexiones TCP/HTTP hacia los servidores. Para sockets TCP directos, puede balancear por IP hash/puerto.
- PostgreSQL se usa para datos transaccionales y S3 para objetos/binaries.

