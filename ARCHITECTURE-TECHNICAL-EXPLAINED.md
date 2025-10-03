# Debuggle Technical Architecture (with Descriptions & Data Paths)

## System Diagram

```mermaid
flowchart TD
    U[User or System<br/>Sends Log/API Request]
    A[FastAPI App<br/>Entry point for all requests]
    B[Exception Handlers<br/>Error management]
    C[CORS Middleware<br/>Cross-origin support]
    D[Rate Limiting (slowapi)<br/>Prevents abuse]
    E[Request Logging Middleware<br/>Tracks requests]
    K[/api/v1/beautify<br/>Beautify Log Endpoint]
    J[/api/v1/tiers<br/>Service Tiers Endpoint]
    I[/health<br/>Health Check Endpoint]
    L[/<br/>Root Endpoint]
    F[LogProcessor<br/>Main log processing logic]
    G[Models (Pydantic)<br/>Data validation/serialization]
    H[Config/Settings<br/>App configuration]

    U --> A
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

---

## Component Descriptions & Example Data Paths

### 1. User or System
- **Description:** The client (could be a developer, end user, or another system) that sends HTTP requests to Debuggle.
- **Example Data Path:** JSON payload with logs or API requests sent to endpoints like `/api/v1/beautify`.

---

### 2. FastAPI App
- **Description:** The main web server handling all incoming requests, routing them to the correct endpoint and managing middleware.
- **Example Data Path:** Receives requests, applies middleware (CORS, rate limiting, logging), and forwards to endpoint handler.

---

### 3. Exception Handlers
- **Description:** Capture and format errors into standardized responses for the client.
- **Example Data Path:** If an error occurs anywhere in request processing, it is caught and returned as a friendly JSON error message.

---

### 4. CORS Middleware
- **Description:** Allows web clients from different domains to access the API safely.
- **Example Data Path:** If a browser requests from another domain, CORS headers are added so the browser allows the response.

---

### 5. Rate Limiting (slowapi)
- **Description:** Ensures no client can overwhelm the service by sending too many requests.
- **Example Data Path:** If a user exceeds allowed requests, receives a 429 Too Many Requests error.

---

### 6. Request Logging Middleware
- **Description:** Optionally logs details about every request (method, path, time taken) for monitoring and debugging.
- **Example Data Path:** Each request’s details may be printed in debug mode or sent to a log file/system.

---

### 7. Endpoints

#### a. `/api/v1/beautify`
- **Description:** Accepts logs or stack traces, cleans and beautifies them, adds syntax highlighting, tags, summaries.
- **Example Data Path:**  
  - Input:  
    ```json
    {
      "log_input": "Traceback (most recent call last): ...",
      "options": { "highlight": true, "summarize": true }
    }
    ```  
  - Processing: Validated → Rate limited → Passed to LogProcessor → Response built with Models.
  - Output:  
    ```json
    {
      "cleaned_log": "...",
      "summary": "...",
      "tags": ["error", "python"],
      "metadata": {...}
    }
    ```

#### b. `/api/v1/tiers`
- **Description:** Returns a list of available service tiers and features.
- **Example Data Path:**  
  - Input: `GET /api/v1/tiers`
  - Output:  
    ```json
    {
      "tiers": [
        { "name": "Trace Level", "features": ["Beautify logs", "Syntax highlighting"] },
        ...
      ]
    }
    ```

#### c. `/health`
- **Description:** Reports service health and version.
- **Example Data Path:**  
  - Input: `GET /health`
  - Output:  
    ```json
    {
      "status": "ok",
      "service": "Debuggle",
      "version": "1.0.0"
    }
    ```

#### d. `/`
- **Description:** Returns basic service info, including available endpoints.
- **Example Data Path:**  
  - Input: `GET /`
  - Output:  
    ```json
    {
      "service": "Debuggle",
      "version": "1.0.0",
      "status": "running",
      "docs": "/docs",
      "health": "/health",
      "api": "/api/v1"
    }
    ```

---

### 8. LogProcessor
- **Description:** The core logic for cleaning, analyzing, and beautifying logs.
- **Example Data Path:** Receives log data from the endpoint, returns cleaned log, summary, tags, and metadata.

---

### 9. Models (Pydantic)
- **Description:** Define the shape of requests and responses, handle data validation, and serialization.
- **Example Data Path:** Incoming requests are validated; outgoing responses are formatted to match the schema.

---

### 10. Config/Settings
- **Description:** Centralizes configuration for the application (rate limits, debug mode, etc.).
- **Example Data Path:** All components read settings dynamically (e.g., rate limits, debug flag) to adjust their behavior.

---

## Example Data Paths for Common Ingestions

- **Beautify Log:**  
  User → FastAPI App (middleware/handlers) → `/api/v1/beautify` → LogProcessor → Models → Response

- **Get Service Tiers:**  
  User → FastAPI App → `/api/v1/tiers` → Models → Response

- **Health Check:**  
  User → FastAPI App → `/health` → Models → Response

---

This document gives both a technical diagram and practical context for each part of Debuggle’s processing and main API flows
