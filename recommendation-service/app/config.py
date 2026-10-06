import os


MOVIE_SERVICE_URL = os.getenv(
    "MOVIE_SERVICE_URL",
    "http://localhost:8000"
)

QDRANT_HOST = os.getenv(
    "QDRANT_HOST",
    "localhost"
)

QDRANT_PORT = int(
    os.getenv(
        "QDRANT_PORT",
        "6333"
    )
)