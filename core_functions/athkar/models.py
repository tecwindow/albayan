from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AthkarCategory(Base):
    __tablename__ = 'athkar_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    audio_path = Column(String, unique=True)
    from_time = Column(String)
    to_time = Column(String)
    play_interval = Column(Integer, default=5)
    audio_athkar_enabled = Column(Integer, default=0)
    text_athkar_enabled = Column(Integer, default=0)
    
    text_athkars = relationship('TextAthkar', back_populates='category', cascade='all, delete-orphan')
    audio_athkars = relationship('AudioAthkar', back_populates='category', cascade='all, delete-orphan')

class TextAthkar(Base):
    __tablename__ = 'text_athkar'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey('athkar_categories.id', ondelete='CASCADE'))
    
    category = relationship('AthkarCategory', back_populates='text_athkars')

    __table_args__ = (UniqueConstraint('name', 'category_id'), UniqueConstraint('text', 'category_id'))

class AudioAthkar(Base):
    __tablename__ = 'audio_athkar'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    audio_file_name = Column(String, nullable=False)
    description = Column(Text)
    is_enabled = Column(Integer, default=1)
    category_id = Column(Integer, ForeignKey('athkar_categories.id', ondelete='CASCADE'))
    
    category = relationship('AthkarCategory', back_populates='audio_athkars')

    __table_args__ = (UniqueConstraint('audio_file_name', 'category_id'),)
