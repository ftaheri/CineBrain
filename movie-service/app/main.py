from fastapi import FastAPI
from app.database import engine, Base
import app.models
from app.routes import movies

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="Movie Service"
)

app.include_router(
    movies.router
)

@app.get("/health")
def health():
    return {
        "status":"ok"
    }

@app.get("/")
def home():
    return {
        "message":"Movie service running"
    }
