from fastapi import APIRouter, Depends, Query
from auth.dependencies import get_current_active_user


router = APIRouter()


@router.get("/{user_id}")
async def Get_user(user_id, current_user: dict = Depends(get_current_active_user)):
    return {"message": f"Hello user {user_id}"}

@router.post("")
async def Post_user(current_user: dict = Depends(get_current_active_user)):
    return {"message": "CREATE DATABASE"}