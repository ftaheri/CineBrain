from fastapi import FastAPI

from app.routes import recommendation


app = FastAPI(
    title="CineBrain Hybrid Recommendation Service",
    description=(
        "Combines collaborative filtering and content-based recommendations."
    ),
    version="1.0.0"
)


app.include_router(
    recommendation.router
)


@app.get("/")
def health_check():

    return {
        "service": "hybrid-recommendation-service",
        "status": "running"
    }