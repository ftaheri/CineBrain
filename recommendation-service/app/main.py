from fastapi import FastAPI
from app.routes import recommendations


app = FastAPI(
    title="Recommendation Service"
)


app.include_router(
    recommendations.router
)


@app.get("/")
def home():
    return {
        "message": "Recommendation service running"
    }