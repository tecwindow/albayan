from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Define the SQLAlchemy base.
Base = declarative_base()

class TasbihEntry(Base):
    __tablename__ = 'tasbih_entries'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    counter = Column(Integer, default=0)
