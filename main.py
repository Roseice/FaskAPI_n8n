from fastapi import FastAPI
from routers.api_v1.routers import router


description = """
# 這只是 Demo 用的
暫無
"""
app = FastAPI(
    title="FastAPI測試",
    version="1.0.0",
    description=description
)

app.include_router(router, prefix="/api/v1")