from sqlalchemy import create_engine
from .models import Base

def init_db(db_path: str):
    engine = create_engine("sqlite:///"+db_path)
    Base.metadata.create_all(engine)
    return engine
