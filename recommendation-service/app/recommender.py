from surprise import Dataset
from surprise import Reader
from surprise import SVD


class MovieRecommender:

    def __init__(self):

        self.model = SVD()


    def train(self, ratings):

        reader = Reader(
            rating_scale=(0.5,5)
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


    def predict(
        self,
        user_id,
        movie_id
    ):

        return self.model.predict(
            user_id,
            movie_id
        ).est