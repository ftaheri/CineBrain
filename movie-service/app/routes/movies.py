from fastapi import APIRouter
from app.database import SessionLocal
from app.models import Movie

router = APIRouter()

@router.get("/movies/{movie_id}")
def get_movie(movie_id:int):

    db = SessionLocal()

    movie = (
        db.query(Movie)
        .filter(Movie.id == movie_id)
        .first()
    )

    db.close()

    return movie

@router.get("/search")
def search_movies(query:str):

    db = SessionLocal()

    movies = (
        db.query(Movie)
        .filter(
            Movie.title.ilike(
                f"%{query}%"
            )
        )
        .limit(20)
        .all()
    )

    db.close()

    return movies