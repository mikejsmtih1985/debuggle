```mermaid
flowchart TD
    A[You send a log or request]
    B[Debuggle's "Receptionist" (FastAPI)]
    C["Bouncer" checks rate (Rate Limiter)]
    D["Brain" cleans up log (LogProcessor)]
    E["Translator" makes results human-friendly (Models)]
    F[You get a neat, easy-to-read result!]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
```