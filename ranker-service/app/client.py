import requests


from app.config import RECOMMENDATION_SERVICE_URL


def get_collaborative_recommendations(
    user_id: int,
    top_k: int = 10
):
    response = requests.get(
        f"{RECOMMENDATION_SERVICE_URL}/recommendations/user/{user_id}",
        params={
            "top_k": top_k
        }
    )

    response.raise_for_status()

    return response.json()


def get_content_recommendations(
    movie_id: int,
    top_k: int = 10
):
    response = requests.get(
        f"{RECOMMENDATION_SERVICE_URL}/recommendations/movie/{movie_id}",
        params={
            "top_k": top_k
        }
    )

    response.raise_for_status()

    return response.json()