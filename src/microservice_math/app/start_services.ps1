# PowerShell script to start all microservices in parallel
# 1. Start the database microservice (FastAPI on port 7000)
# 2. Start the math microservice (Flask, via py -m app.main, on port 5000)
# 3. Start the gateway (FastAPI, via uvicorn, on port 8000)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Start DB microservice
Start-Process -NoNewWindow -WorkingDirectory $scriptDir -FilePath "uvicorn" -ArgumentList "app.db:app --host 0.0.0.0 --port 7000 --reload"

# Start math microservice
Start-Process -NoNewWindow -WorkingDirectory $scriptDir -FilePath "py" -ArgumentList "-m app.main"

# Start gateway
Start-Process -NoNewWindow -WorkingDirectory $scriptDir -FilePath "uvicorn" -ArgumentList "gateway:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "All services started in parallel."
