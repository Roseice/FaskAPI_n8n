from fastapi import APIRouter


router = APIRouter()


@router.get("/{user_id}")
async def Get_user(user_id):
    return {"message": f"Hello user {user_id}"}

@router.post("")
async def Post_user():
    return {"message": "CREATE DATABASE"}