from fastapi import APIRouter
from app.embedder import Embedder
from qdrant_client.models import Filter
from app.qdrant_client import client

router = APIRouter()
embedder = Embedder()

@router.post("/embed")
def embed(body: dict):
    vector = embedder.embed(
        body["text"]
    )

    return {
        "embedding": vector
    }


@router.get("/search")
def semantic_search(query: str):

    vector = embedder.embed(query)

    hits = client.search(

        collection_name="movies",

        query_vector=vector,

        limit=5

    )

    return hits