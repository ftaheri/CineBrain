from fastapi import APIRouter

router = APIRouter()

@router.get("/recommendations/user/{user_id}")
def recommend(user_id:int):

    return {
        "user_id": user_id,
        "recommendations": []
    }