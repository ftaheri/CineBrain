import requests


MOVIE_SERVICE = (
    "http://localhost:8000"
)


def get_movie(movie_id):

    response = requests.get(
        f"{MOVIE_SERVICE}/movies/{movie_id}"
    )

    return response.json()