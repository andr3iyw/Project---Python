from fastapi import FastAPI, Request
import httpx

app = FastAPI()
MATH_SERVICE_URL = 'http://localhost:5000'

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
