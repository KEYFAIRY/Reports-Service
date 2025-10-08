from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MusicalErrorModel(Base):
    __tablename__ = "MusicalError"

    id = Column(Integer, primary_key=True, autoincrement=True)
    min_sec = Column(String(50), nullable=False)
    note_played = Column(String(10), nullable=True)
    note_correct = Column(String(10), nullable=True)
    id_practice = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "min_sec", "note_played", "note_correct", "id_practice",
            name="uq_musical_error"
        ),
    )