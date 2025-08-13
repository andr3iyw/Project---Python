from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()
MATH_SERVICE_URL = "http://math_service:5002"
AUTH_SERVICE_URL = "http://auth_service:5001"


@app.get("/")
async def root():
    return {"message": "API Gateway running..."}


@app.api_route(
    "/math/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_math(path: str, request: Request):
    # Extract username from cookies/session if available
    username = request.cookies.get("session_username")
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    if username:
        headers["X-Username"] = username
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=f"{MATH_SERVICE_URL}/{path}",
            headers=headers,
            params=request.query_params,
            content=await request.body(),
        )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
    )


@app.api_route(
    "/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_auth(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=f"{AUTH_SERVICE_URL}/{path}",
            headers={
                k: v for k, v in request.headers.items() if k.lower() != "host"
            },
            params=request.query_params,
            content=await request.body(),
        )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
    )
