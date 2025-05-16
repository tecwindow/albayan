# -*- coding: utf-8 -*-

from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Quran, QuranBase
from .types import QuranFontType, NavigationMode, Ayah
from pathlib import Path


class QuranManager:
    MAX_PAGE = 604
    MAX_SURAH = 114
    MAX_JUZ = 30
    MAX_HIZB = 60
    MAX_QUARTER = 240

    def __init__(self, font_type: QuranFontType, navigation_mode: NavigationMode = NavigationMode.PAGE):
        self._font_type = font_type
        self.db_path: Path = font_type.database
        self._create_engine_and_session()

        self._navigation_mode = None
        self.current_position = 1
        self.max_position = None
        self.navigation_mode = navigation_mode  # setter

    def _create_engine_and_session(self):
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        QuranBase.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session: Session = self.Session()

    @property
    def font_type(self) -> QuranFontType:
        return self._font_type

    @font_type.setter
    def font_type(self, value: QuranFontType):
        if value != self._font_type:
            self._font_type = value
            self.db_path = value.database
            self._create_engine_and_session()

    @property
    def navigation_mode(self) -> NavigationMode:
        return self._navigation_mode

    @navigation_mode.setter
    def navigation_mode(self, mode: NavigationMode):
        if mode != self._navigation_mode:
            self._navigation_mode = mode
            self.max_position = self.get_max_for_navigation(mode)
            self.current_position = 1

    @classmethod
    def get_max_for_navigation(cls, mode: NavigationMode) -> int:
        max_values = {
            NavigationMode.PAGE: cls.MAX_PAGE,
            NavigationMode.SURAH: cls.MAX_SURAH,
            NavigationMode.JUZ: cls.MAX_JUZ,
            NavigationMode.HIZB: cls.MAX_HIZB,
            NavigationMode.QUARTER: cls.MAX_QUARTER,
        }
        return max_values.get(mode)

    def get_page(self, page_number: int) -> List[Ayah]:
        self.navigation_mode = NavigationMode.PAGE
        rows = (
            self.session.query(Quran)
            .filter(Quran.page == page_number)
            .order_by(Quran.number)
            .all()
        )
        return [self._row_to_ayah(row) for row in rows]

    def get_surah(self, surah_number: int) -> List[Ayah]:
        self.navigation_mode = NavigationMode.SURAH
        rows = (
            self.session.query(Quran)
            .filter(Quran.sura_number == surah_number)
            .order_by(Quran.numberInSurah)
            .all()
        )
        return [self._row_to_ayah(row) for row in rows]

    def get_juz(self, juz_number: int) -> List[Ayah]:
        self.navigation_mode = NavigationMode.JUZ
        rows = (
            self.session.query(Quran)
            .filter(Quran.juz == juz_number)
            .order_by(Quran.number)
            .all()
        )
        return [self._row_to_ayah(row) for row in rows]

    def get_hizb(self, hizb_number: int) -> List[Ayah]:
        self.navigation_mode = NavigationMode.HIZB
        rows = (
            self.session.query(Quran)
            .filter(Quran.hizb == hizb_number)
            .order_by(Quran.number)
            .all()
        )
        return [self._row_to_ayah(row) for row in rows]

    def get_quarter(self, quarter_number: int) -> List[Ayah]:
        self.navigation_mode = NavigationMode.QUARTER
        rows = (
            self.session.query(Quran)
            .filter(Quran.hizbQuarter == quarter_number)
            .order_by(Quran.number)
            .all()
        )
        return [self._row_to_ayah(row) for row in rows]

    def get_current_content(self) -> List[Ayah]:
        mode_to_method = {
            NavigationMode.PAGE: self.get_page,
            NavigationMode.SURAH: self.get_surah,
            NavigationMode.JUZ: self.get_juz,
            NavigationMode.HIZB: self.get_hizb,
            NavigationMode.QUARTER: self.get_quarter,
        }
        getter = mode_to_method.get(self._navigation_mode, self.get_page)
        return getter(self.current_position)

    def next(self) -> list[Ayah]:
        if self.current_position < self.max_position:
            self.current_position += 1
        return self.get_current_content()

    def back(self) -> list[Ayah]:
        if self.current_position > 1:
            self.current_position -= 1
        return self.get_current_content()

    def go_to(self, position: int) -> List[Ayah]:
        if 1 <= position <= self.max_position:
            self.current_position = position
        elif position < 1:
            self.current_position = 1
        else:
            self.current_position = self.max_position
        return self.get_current_content()
    
    def _row_to_ayah(self, row) -> Ayah:
        return Ayah(
            number=row.number,
            text=row.text,
            sura_name=row.sura_name,
            sura_number=row.sura_number,
            number_in_surah=row.numberInSurah,
            juz=row.juz,
            hizb=row.hizb,
            hizbQuarter=row.hizbQuarter,
            page=row.page,
            sajda=row.sajda,
            sajdaObligation=row.sajdaObligation,
        )
