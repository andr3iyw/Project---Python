# Math Microservice Project

This project is split into three microservices and a Streamlit GUI:
- **Auth Microservice** (Flask, port 5001)
- **Math Microservice** (Flask, port 5002)
- **Gateway Microservice** (FastAPI, port 8000)
- **Streamlit GUI** (interacts via Gateway)

## Prerequisites
- Python 3.10+
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```
  (You may also need to install `uvicorn`, `httpx`, and `streamlit` if not in requirements.txt)

## How to Run Everything

### 1. Start the Auth Microservice
```
cd src/auth_service
python app.py
```
This runs the auth service on port 5001.

### 2. Start the Math Microservice
```
cd src/math_service
python app.py
```
This runs the math service on port 5002.

### 3. Start the Gateway Microservice
```
cd src/microservice_math/app
uvicorn gateway:app --port 8000
```
This runs the FastAPI gateway on port 8000.

### 4. Start the Streamlit GUI
```
cd src/microservice_math
streamlit run gui.py
```
The GUI will interact with the gateway at http://localhost:8000.

## Usage
- Use the GUI to register/login and perform math operations.
- All requests go through the gateway, which routes them to the correct microservice.

## Notes
- Make sure all services are running before using the GUI.
- The database file is shared between services (default: `microservice_math.db`).
- If you need to initialize the database, run the `init_db` function from either microservice.
# Project---Python
Proiect Python 
