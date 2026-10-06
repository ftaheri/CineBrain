from app.qdrant_client import client

class ContentBasedRecommender:

    def __init__(
        self,
        collection_name: str = "movies"
    ):
        self.client = client
        self.collection_name = collection_name

    def recommend(
        self,
        movie_id: int,
        top_k: int = 10
    ):

        # Get the movie's embedding from Qdrant
        points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[movie_id],
            with_vectors=True,
            with_payload=True
        )

        if not points:
            return []

        movie = points[0]

        if movie.vector is None:
            return []

        # Search Qdrant for similar movie embeddings
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=movie.vector,
            limit=top_k + 1,
            with_payload=True
        ).points

        recommendations = []

        for result in search_results:

            # Don't recommend the movie itself
            if result.id == movie_id:
                continue

            payload = result.payload or {}

            recommendations.append({
                "movie_id": payload.get("movie_id", result.id),
                "title": payload.get("title", ""),
                "score": round(float(result.score), 4)
            })

            if len(recommendations) >= top_k:
                break

        return recommendations