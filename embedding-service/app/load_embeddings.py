from qdrant_client.models import PointStruct

from app.database import SessionLocal
from app.models import Movie
from app.embedder import Embedder
from app.qdrant_client import client
from app.create_collection import create_collection_if_not_exists

create_collection_if_not_exists()

BATCH_SIZE = 1000

db = SessionLocal()
embedder = Embedder()
movies = db.query(Movie).all()
points = []
iteration = 1


print(f"Found {len(movies)} movies to embed.")

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

    if iteration % BATCH_SIZE == 0 or iteration == len(movies):
        print(f"Uploading batch {iteration // BATCH_SIZE}...")
        client.upsert(
            collection_name="movies",
            points=points
        )
        print(f"Uploaded batch {iteration // BATCH_SIZE}.")
        points = []

    iteration += 1
    

print("Finished.")