from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PracticeModel(Base):
    __tablename__ = "Practice"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(50), nullable=False)
    time = Column(String(50), nullable=False)
    num_postural_errors = Column(Numeric, nullable=True)
    num_musical_errors = Column(Numeric, nullable=True)
    duration = Column(Numeric, nullable=True)
    bpm = Column(Integer, nullable=False)
    id_student = Column(String(128), nullable=False)
    id_scale = Column(Integer, nullable=False)