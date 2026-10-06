from qdrant_client.models import Distance, VectorParams

from app.qdrant_client import client, COLLECTION_NAME


def create_collection_if_not_exists():
    collections = client.get_collections().collections

    collection_names = [
        collection.name
        for collection in collections
    ]

    if COLLECTION_NAME in collection_names:
        print(
            f"Collection '{COLLECTION_NAME}' already exists."
        )
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    print(
        f"Created collection '{COLLECTION_NAME}'."
    )


if __name__ == "__main__":
    create_collection_if_not_exists()