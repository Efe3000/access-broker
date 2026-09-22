from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:////data/approvals.db")
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True)
    status = Column(String, default="pending")
    path = Column(String)
    sub = Column(String)
    created_at = Column(Float)

Base.metadata.create_all(engine)