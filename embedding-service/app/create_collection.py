from qdrant_client.models import Distance
from qdrant_client.models import VectorParams

from app.qdrant_client import client

client.recreate_collection(
    collection_name="movies",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)