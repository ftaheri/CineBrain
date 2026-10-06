import os
import pickle

from surprise import Dataset
from surprise import Reader
from surprise import SVD

from app.movie_client import get_movie

MODEL_PATH = "models/recommender.pkl"


class CollaborativeRecommender:

    def __init__(self, ratings=None):

        if os.path.exists(MODEL_PATH):
            print("Loading collaborative model...")
            with open(MODEL_PATH, "rb") as f:
                saved_model = pickle.load(f)

            self.model = saved_model["model"]
            self.movie_ids = saved_model["movie_ids"]
            self.rated_movies = saved_model["rated_movies"]

            print("Loaded collaborative model.")

        else:
            print("No saved model found. Initializing a new collaborative model.")
            self.model = SVD()
            self.movie_ids = set()
            self.rated_movies = {}

    def train(self, ratings):
        print("Training collaborative model...")
        reader = Reader(
            rating_scale=(0.5, 5)
        )

        data = Dataset.load_from_df(
            ratings[
                [
                    "userId",
                    "movieId",
                    "rating"
                ]
            ],
            reader
        )

        trainset = data.build_full_trainset()

        self.model.fit(trainset)
        print("Collaborative model training completed.")

        # All movie IDs known by the model
        self.movie_ids = set(
            ratings["movieId"].unique()
        )

        # Movies each user has already rated
        self.rated_movies = (
            ratings
            .groupby("userId")["movieId"]
            .apply(set)
            .to_dict()
        )

        self.save()

    def save(self):
        os.makedirs(
            os.path.dirname(MODEL_PATH),
            exist_ok=True
        )

        with open(MODEL_PATH, "wb") as f:

            pickle.dump(
                {
                    "model": self.model,
                    "movie_ids": self.movie_ids,
                    "rated_movies": self.rated_movies
                },
                f
            )

        print("Collaborative model saved.")

    def predict(
        self,
        user_id: int,
        movie_id: int
    ):

        return self.model.predict(
            user_id,
            movie_id
        ).est

    def recommend(
        self,
        user_id: int,
        top_k: int = 10
    ):

        rated_movies = self.rated_movies.get(
            user_id,
            set()
        )

        predictions = []

        for movie_id in self.movie_ids:

            if movie_id in rated_movies:
                continue

            predicted_rating = self.predict(
                user_id,
                movie_id
            )

            predictions.append({
                "movie_id": int(movie_id),
                "score": round(
                    float(predicted_rating),
                    4
                )
            })

        predictions.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        predictions = predictions[:top_k]

        recommendations = []

        for prediction in predictions:

            movie = get_movie(
                prediction["movie_id"]
            )

            recommendations.append({
                "movie_id": prediction["movie_id"],
                "title": movie["title"],
                "score": round(
                    prediction["score"],
                    4
                )
            })

        return recommendations