from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.infrastructure.database.models.base import Base

class StudentModel(Base):
    __tablename__ = "Student"

    uid = Column(String(128), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    piano_level = Column(String(50), nullable=False)

    practices = relationship("PracticeModel", back_populates="student")
