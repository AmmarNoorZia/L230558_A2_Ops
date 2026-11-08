"""Structured history log: only decisions and metadata, never image contents."""
from datetime import datetime, timezone
from pathlib import Path
import os
from sqlalchemy import DateTime, Float, Integer, String, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'instance' / 'visionguard.sqlite3'

class Base(DeclarativeBase):
    pass

class PredictionRecord(Base):
    __tablename__ = 'predictions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    filename: Mapped[str] = mapped_column(String(255))
    verdict: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float)
    ai_probability: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(128))

_engine = None
_sessions = None

def database():
    global _engine, _sessions
    if _engine is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        address = os.getenv('DATABASE_URL') or f'sqlite:///{DB_PATH.as_posix()}'
        if address.startswith('postgres://'):
            address = 'postgresql://' + address[len('postgres://'):]
        _engine = create_engine(address, pool_pre_ping=True)
        _sessions = sessionmaker(_engine, expire_on_commit=False)
        Base.metadata.create_all(_engine)
    return _sessions

def store_prediction(filename, result):
    session_factory = database()
    with session_factory.begin() as session:
        record = PredictionRecord(filename=filename,
            verdict=result['label'], confidence=result['confidence'],
            ai_probability=result['ai_probability'], threshold=result['threshold'],
            model_version=result['model_version'])
        session.add(record)
        session.flush()
        record_id = record.id
    return record_id

def history(limit=50):
    with database()() as session:
        return session.scalars(select(PredictionRecord).order_by(PredictionRecord.id.desc()).limit(limit)).all()

def get_prediction(record_id):
    with database()() as session:
        return session.get(PredictionRecord, record_id)

def database_healthy():
    with database()() as session:
        session.execute(text('SELECT 1'))
    return True
