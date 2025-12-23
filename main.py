import time
from fastapi import FastAPI
from fastapi.middleware import Middleware
from routers.api_v1.routers import router
from starlette.middleware.base import BaseHTTPMiddleware

class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        print(response.headers)
        return response

middleware = [
    Middleware(CustomHeaderMiddleware)
]

description = """
# 這只是 Demo 用的
"""
app = FastAPI(
    title="FastAPI測試",
    version="1.0.0",
    description=description,
    middleware=middleware
)

app.include_router(router, prefix="/api/v1")