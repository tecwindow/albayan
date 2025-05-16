# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

QuranBase = declarative_base()
AyahMapBase = declarative_base()

class Quran(QuranBase):
    __tablename__ = 'quran'

    number = Column(Integer, primary_key=True)  # Ayah number in the whole Quran
    text = Column(Text, nullable=False)
    sura_name = Column(String, nullable=False)
    sura_number = Column(Integer, nullable=False)
    numberInSurah = Column(Integer, nullable=False)  # Ayah number in the surah
    juz = Column(Integer, nullable=False)
    hizb = Column(Integer, nullable=False)
    page = Column(Integer, nullable=False)
    hizbQuarter = Column(Integer, nullable=False)
    sajda = Column(Boolean, default=False)
    sajdaObligation = Column(Boolean, default=False)


class AyahViewMap(AyahMapBase):
    __tablename__ = 'ayah_view_map'

    number = Column(Integer, primary_key=True)  # Unique number of the ayah in the Quran
    text = Column(Text, nullable=False)
    sura_name = Column(String, nullable=False)
    sura_number = Column(Integer, nullable=False)
    number_in_surah = Column(Integer, nullable=False)
    juz = Column(Integer, nullable=False)
    hizb = Column(Integer, nullable=False)
    hizbQuarter = Column(Integer, nullable=False)
    page = Column(Integer, nullable=False)
    first_position = Column(Integer, nullable=False)
    last_position = Column(Integer, nullable=False)
    sajda = Column(Boolean, default=False)
    sajdaObligation = Column(Boolean, default=False)
    