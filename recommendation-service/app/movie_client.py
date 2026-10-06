import requests

from app.config import MOVIE_SERVICE_URL


def get_movie(movie_id: int):
    response = requests.get(
        f"{MOVIE_SERVICE_URL}/movies/{movie_id}"
    )

    response.raise_for_status()

    return response.json()