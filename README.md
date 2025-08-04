# Math Microservice Project

This project is split into three microservices and a Streamlit GUI:

- **Auth Microservice** (Flask, port 5001): handles user registration and login
- **Math Microservice** (Flask, port 5002): computes power, factorial, and Fibonacci operations
- **Gateway Microservice** (FastAPI, port 8000): acts as a reverse proxy between GUI and backend services
- **Streamlit GUI** (port 8501): user interface for interacting with the system

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Install dependencies:
  
  ```
  pip install -r requirements.txt
  ```

---

## How to Run Everything (via Docker)

> Recommended for quick setup and clean dependency management

### 1. Build & Start All Services

From the root directory:
```
docker-compose up --build
```

This launches:
- Flask-based `auth_service` on port **5001**
- Flask-based `math_service` on port **5002**
- FastAPI `gateway` on port **8000**
- Streamlit GUI on port **8501**

### 2. Access the GUI

Open your browser at:  
**[http://localhost:8501](http://localhost:8501)**

---

## Usage

- Use the GUI to register/login and compute mathematical operations.
- All requests flow through the API Gateway, which routes them to the correct microservice.
- Each request is logged into the shared SQLite database (`microservice_math.db`).
- Recent logs can be viewed in the GUI.

---

## Notes

- Ensure all services are running before interacting with the GUI.
- The SQLite database is shared across services using a Docker volume.
- If logs don’t appear, make sure the `request_log` table exists or that the database volume is mounted correctly.