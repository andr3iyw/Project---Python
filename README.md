
# Math Microservice Project

This project is a microservices-based system for user authentication and mathematical computations, with a web GUI. It uses Docker Compose for orchestration.
<img width="1717" height="866" alt="mermaid-diagram-2025-08-14-143337" src="https://github.com/user-attachments/assets/a9657d44-6351-43d3-b0fd-9342b15d3f83" />

## Architecture Overview

- **auth_service** (Flask, port 5001):  
  Handles user registration, login, and authentication. Stores user data and verifies credentials.

- **math_service** (Flask, port 5002):  
  Provides endpoints for mathematical operations: power, factorial, and Fibonacci.  
  - Uses Redis for caching results (optional, controlled by `CACHE_ENABLED`).
  - Logs each request to a shared SQLite database.

- **gateway** (FastAPI, port 8000):  
  Acts as an API gateway/reverse proxy.  
  - Routes requests from the GUI to the appropriate backend service.
  - Adds user context to requests (e.g., username).

- **gui** (Streamlit, port 8501):  
  User interface for registration, login, and performing math operations.  
  - All interactions go through the gateway.

## Data Flow

1. **User interacts with GUI** (registers, logs in, requests math operations).
2. **GUI sends requests to Gateway** (`localhost:8000`).
3. **Gateway forwards requests** to either `auth_service` or `math_service` based on the endpoint.
4. **auth_service** authenticates users.
5. **math_service** performs calculations, optionally caches results in Redis, and logs requests in the shared database.
6. **Results and logs** are returned to the GUI for display.

## Shared Database

- All services use a shared SQLite database (`microservice_math.db`) via a Docker volume (`shared-db`).
- The database stores user data and logs of all math operations.

## Redis Caching

- The math service uses Redis (host: `redis`, port: `6379`) for caching results.
- Caching is controlled by the `CACHE_ENABLED` flag in `math_service/app.py`.

## How to Run Everything (via Docker)

### Prerequisites

- Python 3.10+
- Docker & Docker Compose

### 1. Build & Start All Services

From the root directory, run:
```powershell
docker-compose up --build
```
This will:
- Build and start all microservices and the GUI.
- Set up the shared database volume.

### 2. Access the GUI

Open your browser at:  
**http://localhost:8501**

### 3. Stopping Services

To stop all services:
```powershell
docker-compose down
```

## Usage

- Register and log in via the GUI.
- Perform math operations (power, factorial, Fibonacci).
- View recent logs in the GUI.
- All requests are routed through the gateway for security and logging.

## Troubleshooting

- If you see `ModuleNotFoundError: No module named 'redis'`, ensure `redis` is in `requirements.txt` and rebuild with `docker-compose build --no-cache`.
- If logs do not appear, check that the database volume is mounted and the `request_log` table exists.
- Make sure all services are running (`docker-compose ps`).

## File Structure

- `src/auth_service/`: Auth microservice code
- `src/math_service/`: Math microservice code
- `src/gateway/app/`: API gateway code
- `src/gateway/gui.py`: Streamlit GUI code
- `requirements.txt`: Python dependencies (including `redis`)
- `docker-compose.yml`: Service orchestration
- `Dockerfile.*`: Docker build files for each service

## Notes

- All services communicate over the Docker network using service names (e.g., `math_service`, `auth_service`).
- The shared database volume ensures persistent and consistent data across services.
- Redis must be running and accessible for caching to work.
