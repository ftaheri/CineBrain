from fastapi import FastAPI

from app.routes.embeddings import router

app = FastAPI()

app.include_router(router)