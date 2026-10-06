from app.client import (
    get_collaborative_recommendations,
    get_content_recommendations
)


class HybridRecommender:

    def __init__(
        self,
        collaborative_weight: float = 0.7,
        content_weight: float = 0.3
    ):
        if collaborative_weight + content_weight != 1.0:
            raise ValueError(
                "Weights must sum to 1.0"
            )

        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight

    def normalize_scores(self, recommendations):
        """
        Min-max normalize recommendation scores to [0, 1].
        """

        if not recommendations:
            return []

        scores = [
            recommendation["score"]
            for recommendation in recommendations
        ]

        min_score = min(scores)
        max_score = max(scores)

        # All scores are identical
        if max_score == min_score:
            for recommendation in recommendations:
                recommendation["normalized_score"] = 1.0

            return recommendations

        for recommendation in recommendations:
            score = recommendation["score"]

            recommendation["normalized_score"] = (
                (score - min_score)
                / (max_score - min_score)
            )

        return recommendations

    def combine(
        self,
        collaborative,
        content
    ):
        # Combine collaborative and content-based recommendations into one ranked list.
        collaborative = self.normalize_scores(
            collaborative
        )

        content = self.normalize_scores(
            content
        )

        combined = {}

        # Add collaborative recommendations
        for recommendation in collaborative:

            movie_id = recommendation["movie_id"]

            combined[movie_id] = {
                "movie_id": movie_id,
                "collaborative_score": recommendation[
                    "normalized_score"
                ],
                "content_score": 0.0,
                "hybrid_score": (
                    self.collaborative_weight
                    * recommendation["normalized_score"]
                )
            }

            # Preserve title if available
            if "title" in recommendation:
                combined[movie_id]["title"] = (
                    recommendation["title"]
                )

        # Add content recommendations
        for recommendation in content:

            movie_id = recommendation["movie_id"]

            content_score = recommendation[
                "normalized_score"
            ]

            if movie_id in combined:

                combined[movie_id]["content_score"] = (
                    content_score
                )

                combined[movie_id]["hybrid_score"] += (
                    self.content_weight
                    * content_score
                )

            else:

                combined[movie_id] = {
                    "movie_id": movie_id,
                    "collaborative_score": 0.0,
                    "content_score": content_score,
                    "hybrid_score": (
                        self.content_weight
                        * content_score
                    )
                }

                if "title" in recommendation:
                    combined[movie_id]["title"] = (
                        recommendation["title"]
                    )

        recommendations = list(
            combined.values()
        )

        recommendations.sort(
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        for recommendation in recommendations:
            recommendation["hybrid_score"] = round(
                recommendation["hybrid_score"],
                4
            )

            recommendation["collaborative_score"] = round(
                recommendation["collaborative_score"],
                4
            )

            recommendation["content_score"] = round(
                recommendation["content_score"],
                4
            )

        return recommendations

    def recommend(
        self,
        user_id: int,
        top_k: int = 10,
        candidate_k: int = 20
    ):
        """
        Generate hybrid recommendations for a user.
        """

        # 1. Get collaborative recommendations
        collaborative_response = (
            get_collaborative_recommendations(
                user_id=user_id,
                top_k=candidate_k
            )
        )

        collaborative = (
            collaborative_response.get(
                "recommendations",
                []
            )
        )

        # 2. Use top collaborative movies as seeds
        # for content-based retrieval.
        content = []

        for recommendation in collaborative[:5]:

            movie_id = recommendation["movie_id"]

            content_response = (
                get_content_recommendations(
                    movie_id=movie_id,
                    top_k=candidate_k
                )
            )

            movie_recommendations = (
                content_response.get(
                    "recommendations",
                    []
                )
            )

            content.extend(
                movie_recommendations
            )

        # 3. Remove duplicate content recommendations
        content = self._remove_deduplicates(
            content
        )

        # 4. Combine both recommendation sources
        recommendations = self.combine(
            collaborative=collaborative,
            content=content
        )

        # 5. Return final Top-K
        return recommendations[:top_k]

    def _remove_deduplicates(self, recommendations):

        movies = {}

        for recommendation in recommendations:

            movie_id = recommendation["movie_id"]

            # Keep the highest score if the same
            # movie appears multiple times.
            if movie_id not in movies:

                movies[movie_id] = recommendation

            elif (
                recommendation["score"]
                > movies[movie_id]["score"]
            ):

                movies[movie_id] = recommendation

        return list(movies.values())