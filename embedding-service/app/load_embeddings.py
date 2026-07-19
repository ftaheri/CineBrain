from qdrant_client.models import PointStruct

from app.database import SessionLocal
from app.models import Movie
from app.embedder import Embedder
from app.qdrant_client import client

BATCH_SIZE = 500

db = SessionLocal()
embedder = Embedder()
movies = db.query(Movie).all()
points = []

for movie in movies:

    text = (
        movie.title
        + " "
        + movie.genres.replace("|", " ")
    )
    vector = embedder.embed(text)

    points.append(
        PointStruct(
            id=movie.id,
            vector=vector,
            payload={
                "title": movie.title,
                "genres": movie.genres
            }
        )
    )

for i in range(0, len(points), BATCH_SIZE):
    batch = points[i:i + BATCH_SIZE]

    client.upsert(
        collection_name="movies",
        points=batch
    )

    print(
        f"Uploaded {i + len(batch)} / {len(points)}"
    )

print("Finished.")