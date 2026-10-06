from fastapi import FastAPI
from app.routes import recommendation


app = FastAPI(
    title="Recommendation Service"
)


app.include_router(
    recommendation.router
)


@app.get("/")
def home():
    return {
        "message": "Recommendation service running"
    }