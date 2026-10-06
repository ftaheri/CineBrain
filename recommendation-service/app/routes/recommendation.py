from fastapi import APIRouter

from app.collaborative_recommender import CollaborativeRecommender
from app.content_recommender import ContentBasedRecommender


router = APIRouter()

collaborative_recommender = CollaborativeRecommender()
content_recommender = ContentBasedRecommender()


@router.get("/recommendations/user/{user_id}")
def recommend_for_user(
    user_id: int,
    top_k: int = 10
):
    """
    Collaborative filtering recommendations using SVD.
    """

    recommendations = collaborative_recommender.recommend(
        user_id=user_id,
        top_k=top_k
    )

    return {
        "user_id": user_id,
        "recommendations": recommendations
    }


@router.get("/recommendations/movie/{movie_id}")
def recommend_similar_movies(
    movie_id: int,
    top_k: int = 10
):
    """
    Content-based recommendations using Qdrant embeddings.
    """

    recommendations = content_recommender.recommend(
        movie_id=movie_id,
        top_k=top_k
    )

    return {
        "movie_id": movie_id,
        "recommendations": recommendations
    }