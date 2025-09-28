from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base

class PracticeModel(Base):
    __tablename__ = "Practice"

    id = Column(Integer, primary_key=True, autoincrement=True)
    practice_datetime = Column(DateTime, nullable=False)
    num_postural_errors = Column(Numeric, nullable=True)
    num_musical_errors = Column(Numeric, nullable=True)
    duration = Column(Numeric, nullable=True)
    bpm = Column(Integer, nullable=False)
    id_student = Column(String(128), ForeignKey("Student.uid"), nullable=False)
    id_scale = Column(Integer, nullable=False)

    student = relationship("StudentModel", back_populates="practices")
