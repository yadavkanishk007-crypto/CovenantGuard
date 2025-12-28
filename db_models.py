from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String)
    overall_risk = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("CovenantResult", back_populates="evaluation",  cascade="all, delete-orphan" )


class CovenantResult(Base):
    __tablename__ = "covenant_results"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)

    covenant_name = Column(String, nullable=False)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    status = Column(String, nullable=False)

    evaluation = relationship("Evaluation", back_populates="results")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # admin | operator | viewer

