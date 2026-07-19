from sqlalchemy import Column, Integer, String
from app.database import Base


class Movie(Base):

    __tablename__ = "movies"

    id = Column(
        Integer,
        primary_key=True
    )

    title = Column(
        String
    )

    genres = Column(
        String
    )