from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MusicalErrorModel(Base):
    __tablename__ = "MusicalError"

    id = Column(Integer, primary_key=True, autoincrement=True)
    min_sec = Column(String(50), nullable=False)
    note_played = Column(String(10), nullable=True)
    note_correct = Column(String(10), nullable=True)
    id_practice = Column(Integer, nullable=False)
