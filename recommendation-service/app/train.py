import pandas as pd
import pickle

from app.recommender import MovieRecommender


ratings = pd.read_csv(
    "data/ratings.csv"
)


model = MovieRecommender()

model.train(
    ratings
)


pickle.dump(
    model,
    open(
        "models/recommender.pkl",
        "wb"
    )
)