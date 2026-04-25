from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///./history.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class AnalysisRun(Base):
    __tablename__ = "runs"
    id            = Column(Integer, primary_key=True, index=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    analysis      = Column(Text)
    gaps          = Column(Text)
    enhanced_resume = Column(Text)
    job_suggestions = Column(Text)

Base.metadata.create_all(bind=engine)

def save_run(data: dict) -> int:
    db = SessionLocal()
    run = AnalysisRun(**data)
    db.add(run)
    db.commit()
    db.refresh(run)
    db.close()
    return run.id

def get_all_runs():
    db = SessionLocal()
    runs = db.query(AnalysisRun).order_by(AnalysisRun.created_at.desc()).all()
    db.close()
    return runs

def get_run_by_id(run_id: int):
    db = SessionLocal()
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    db.close()
    return run