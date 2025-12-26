from fastapi import APIRouter
from routers.api_v1.user import router as user_router
from routers.api_v1.data import router as data_router
from routers.api_v1.n8n import router as n8n_router
from auth.dependencies import router as token_data

router = APIRouter()

router.include_router(n8n_router, prefix="/n8n", tags=["n8n"])
router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(data_router, prefix="/data", tags=["data"])
router.include_router(token_data, prefix="/token", tags=["token"])  