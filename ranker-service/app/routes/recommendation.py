from fastapi import APIRouter

from app.hybrid import HybridRecommender


router = APIRouter()

hybrid_recommender = HybridRecommender(
    collaborative_weight=0.7,
    content_weight=0.3
)


@router.get("/recommendations/user/{user_id}")
def recommend(
    user_id: int,
    top_k: int = 10
):

    recommendations = hybrid_recommender.recommend(
        user_id=user_id,
        top_k=top_k
    )

    return {
        "user_id": user_id,
        "recommendations": recommendations
    }