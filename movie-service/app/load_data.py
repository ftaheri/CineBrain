import pandas as pd
from app.database import SessionLocal
from app.models import Movie

df = pd.read_csv(
    "data/movies.csv"
)

db = SessionLocal()

for _, row in df.iterrows():

    movie = Movie(
        id=row["movieId"],
        title=row["title"],
        genres=row["genres"]
    )

    db.add(movie)

db.commit()

db.close()