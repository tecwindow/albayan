from sqlalchemy import create_engine
from .models import Base

def init_db(db_url='sqlite:///athkar.db'):
    engine = create_engine("sqlite:///"+db_url)
    Base.metadata.create_all(engine)
    return engine
