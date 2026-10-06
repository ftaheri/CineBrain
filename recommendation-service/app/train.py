import pickle
import pandas as pd

from app.collaborative_recommender import CollaborativeRecommender


RATINGS_PATH = "data/ratings.csv"

ratings = pd.read_csv(RATINGS_PATH)

recommender = CollaborativeRecommender()

recommender.train(ratings)
