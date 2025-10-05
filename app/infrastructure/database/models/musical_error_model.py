from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MusicalErrorModel(Base):
    __tablename__ = "MusicalError"

    id = Column(Integer, primary_key=True, autoincrement=True)
    min_sec = Column(String(50), nullable=False)
    missed_note = Column(String(10), nullable=True)
    id_practice = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "min_sec", "missed_note", "id_practice",
            name="uq_musical_error"
        ),
    )