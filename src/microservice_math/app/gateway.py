from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()
MATH_SERVICE_URL = 'http://localhost:5000'
DB_SERVICE_URL = 'http://localhost:7000'

@app.get("/")
async def root():
    return {"message": "API Gateway running..."}

@app.api_route("/math/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_math(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=f"{MATH_SERVICE_URL}/math/{path}",
            headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
            params=request.query_params,
            content=await request.body()
        )
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))

# Route to forward log data to the DB microservice
@app.post("/log")
async def forward_log(request: Request):
    data = await request.body()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{DB_SERVICE_URL}/log", content=data, headers={k: v for k, v in request.headers.items() if k.lower() != 'host'})
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
