# gateway/app.py
import os
from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

MATH_SERVICE_URL = os.getenv("MATH_SERVICE_URL", "http://math_service:5002")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:5001")

@app.get("/")
async def root():
    return {"message": "API Gateway running..."}

def _forwardable_headers(request: Request):
    # Drop 'host' and hop-by-hop headers
    hop_by_hop = {
        "host", "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "transfer-encoding", "upgrade"
    }
    return {k: v for k, v in request.headers.items() if k.lower() not in hop_by_hop}

@app.api_route("/math/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_math(path: str, request: Request):
    headers = _forwardable_headers(request)
    # We **do not** decode JWT here. We just forward Authorization as-is.
    # If a client wants to send X-Username (legacy), we forward that too.
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=f"{MATH_SERVICE_URL}/{path}",
            headers=headers,
            params=request.query_params,
            content=await request.body(),
        )
    # Avoid streaming hop-by-hop headers back
    filtered = {k: v for k, v in resp.headers.items() if k.lower() not in {"transfer-encoding", "connection"}}
    return Response(content=resp.content, status_code=resp.status_code, headers=filtered, media_type=resp.headers.get("content-type"))

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_auth(path: str, request: Request):
    headers = _forwardable_headers(request)
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=f"{AUTH_SERVICE_URL}/{path}",
            headers=headers,
            params=request.query_params,
            content=await request.body(),
        )
    filtered = {k: v for k, v in resp.headers.items() if k.lower() not in {"transfer-encoding", "connection"}}
    return Response(content=resp.content, status_code=resp.status_code, headers=filtered, media_type=resp.headers.get("content-type"))
