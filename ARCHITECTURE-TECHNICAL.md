```mermaid
flowchart TD
    subgraph API Layer
        A[FastAPI App]
        B[Exception Handlers]
        C[CORS Middleware]
        D[Rate Limiting (slowapi)]
        E[Request Logging Middleware]
    end

    subgraph Processing Layer
        F[LogProcessor]
        G[Models (Pydantic)]
        H[Config/Settings]
    end

    subgraph Endpoints
        I[/health]
        J[/api/v1/tiers]
        K[/api/v1/beautify]
        L[/] 
    end

    A --> B
    A --> C
    A --> D
    A --> E
    A --> I
    A --> J
    A --> K
    A --> L
    K --> F
    F --> G
    A --> H
```