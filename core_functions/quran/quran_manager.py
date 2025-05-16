# -*- coding: utf-8 -*-

from typing import List, Optional
from pathlib import Path
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import func
from .models import Quran, QuranBase
from .types import QuranFontType, NavigationMode, Surah, Ayah


class QuranManager:
    MAX_PAGE    = 604
    MAX_SURAH   = 114
    MAX_JUZ     = 30
    MAX_HIZB    = 60
    MAX_QUARTER = 240

    def __init__(
        self,
        font_type: QuranFontType,
        navigation_mode: NavigationMode = NavigationMode.PAGE
    ):
        """
        Initialize with a font type (determines DB path)
        and an initial navigation mode.
        """
        self._font_type = font_type
        self.db_path: Path = font_type.database
        self._create_engine_and_session()

        self._navigation_mode: Optional[NavigationMode] = None
        self.current_position: int = 1
        self.max_position: int = 1
        self.navigation_mode = navigation_mode

    def _create_engine_and_session(self):
        """(Re)create SQLAlchemy engine and session for the current DB path."""
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        QuranBase.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session: Session = self.Session()

    @property
    def font_type(self) -> QuranFontType:
        return self._font_type

    @font_type.setter
    def font_type(self, value: QuranFontType):
        """
        Change font type (and underlying DB) at runtime.
        Recreates engine and session automatically.
        """
        if value != self._font_type:
            self._font_type = value
            self.db_path    = value.database
            self._create_engine_and_session()

    @property
    def navigation_mode(self) -> NavigationMode:
        return self._navigation_mode  # type: ignore

    @navigation_mode.setter
    def navigation_mode(self, mode: NavigationMode):
        """
        Set navigation mode (PAGE/SURAH/JUZ/etc.) and
        reset current_position to 1 with updated max_position.
        """
        if mode != self._navigation_mode:
            self._navigation_mode = mode
            self.max_position     = self.get_max_for_navigation(mode)
            self.current_position = 1

    @classmethod
    def get_max_for_navigation(cls, mode: NavigationMode) -> int:
        """Return the maximum index for the given navigation mode."""
        return {
            NavigationMode.PAGE:    cls.MAX_PAGE,
            NavigationMode.SURAH:   cls.MAX_SURAH,
            NavigationMode.JUZ:     cls.MAX_JUZ,
            NavigationMode.HIZB:    cls.MAX_HIZB,
            NavigationMode.QUARTER: cls.MAX_QUARTER,
        }.get(mode, cls.MAX_PAGE)

    def get_suras(self) -> List[Surah]:
        """
        Return a list of Surah objects with their number and name.
        """
        rows = (
            self.session.query(
                Quran.sura_number,
                func.REPLACE(Quran.sura_name, "سورة ", "")
            )
            .distinct()
            .order_by(Quran.sura_number)
            .all()
        )
        return [Surah(number=row.sura_number, name=row.sura_name) for row in rows]

    def get_page(self, page_number: int) -> List[Ayah]:
        """Fetch all Ayahs on a given page."""
        self.navigation_mode = NavigationMode.PAGE
        rows = (
            self.session.query(Quran)
            .filter(Quran.page == page_number)
            .order_by(Quran.number)
            .all()
        )
        return [self._row_to_ayah(r) for r in rows]

    def get_surah(self, surah_number: int) -> List[Ayah]:
        """Fetch all Ayahs in a given surah."""
        self.navigation_mode = NavigationMode.SURAH
        rows = (
            self.session.query(Quran)
            .filter(Quran.sura_number == surah_number)
            .order_by(Quran.numberInSurah)
            .all()
        )
        return [self._row_to_ayah(r) for r in rows]

    def get_juz(self, juz_number: int) -> List[Ayah]:
        """Fetch all Ayahs in a given juz."""
        self.navigation_mode = NavigationMode.JUZ
        rows = (
            self.session.query(Quran)
            .filter(Quran.juz == juz_number)
            .order_by(Quran.number)
            .all()
        )
        return [self._row_to_ayah(r) for r in rows]

    def get_hizb(self, hizb_number: int) -> List[Ayah]:
        """Fetch all Ayahs in a given hizb."""
        self.navigation_mode = NavigationMode.HIZB
        rows = (
            self.session.query(Quran)
            .filter(Quran.hizb == hizb_number)
            .order_by(Quran.number)
            .all()
        )
        return [self._row_to_ayah(r) for r in rows]

    def get_quarter(self, quarter_number: int) -> List[Ayah]:
        """Fetch all Ayahs in a given hizbQuarter."""
        self.navigation_mode = NavigationMode.QUARTER
        rows = (
            self.session.query(Quran)
            .filter(Quran.hizbQuarter == quarter_number)
            .order_by(Quran.number)
            .all()
        )
        return [self._row_to_ayah(r) for r in rows]

    def get_current_content(self) -> List[Ayah]:
        """Fetch Ayahs for the current position and mode."""
        return self.get_by_mode(self._navigation_mode, self.current_position)

    def get_by_mode(self, mode: NavigationMode, pos: int) -> List[Ayah]:
        """Dynamic dispatch to the correct getter by mode."""
        dispatch = {
            NavigationMode.PAGE:    self.get_page,
            NavigationMode.SURAH:   self.get_surah,
            NavigationMode.JUZ:     self.get_juz,
            NavigationMode.HIZB:    self.get_hizb,
            NavigationMode.QUARTER: self.get_quarter,
        }
        return dispatch.get(mode, self.get_page)(pos)

    def next(self) -> List[Ayah]:
        """Advance to the next unit (page/surah/etc.) and return its Ayahs."""
        if self.current_position < self.max_position:
            self.current_position += 1
        return self.get_current_content()

    def back(self) -> List[Ayah]:
        """Go back to the previous unit and return its Ayahs."""
        if self.current_position > 1:
            self.current_position -= 1
        return self.get_current_content()

    def go_to(self, position: int) -> List[Ayah]:
        """
        Jump to a specific position (clamped between 1 and max_position)
        and return its Ayahs.
        """
        if position < 1:
            self.current_position = 1
        elif position > self.max_position:
            self.current_position = self.max_position
        else:
            self.current_position = position
        return self.get_current_content()

    def get_range(
        self,
        from_surah: Optional[int] = None,
        from_ayah:  Optional[int] = None,
        to_surah:   Optional[int] = None,
        to_ayah:    Optional[int] = None
    ) -> List[Ayah]:
        """
        Fetch Ayahs between two points:
          - (from_surah, from_ayah) up to (to_surah, to_ayah)
        If one end is omitted, it defaults to start=1 or end=last Ayah.
        """
        # Determine global numbering for start
        start_num = None
        if from_surah is not None:
            sura_ayahs = (
                self.session.query(Quran)
                .filter(Quran.sura_number == from_surah)
                .order_by(Quran.number)
                .all()
            )
            if sura_ayahs:
                # clamp from_ayah
                idx = max(1, min(len(sura_ayahs), from_ayah or 1)) - 1
                start_num = sura_ayahs[idx].number

        # Determine global numbering for end
        end_num = None
        if to_surah is not None:
            sura_ayahs = (
                self.session.query(Quran)
                .filter(Quran.sura_number == to_surah)
                .order_by(Quran.number)
                .all()
            )
            if sura_ayahs:
                idx = max(1, min(len(sura_ayahs), to_ayah or len(sura_ayahs))) - 1
                end_num = sura_ayahs[idx].number

        # Build final query
        query = self.session.query(Quran).order_by(Quran.number)
        if start_num is not None and end_num is not None:
            if start_num > end_num:
                start_num, end_num = end_num, start_num
            query = query.filter(Quran.number.between(start_num, end_num))
        elif start_num is not None:
            query = query.filter(Quran.number >= start_num)
        else:
            query = query.filter(Quran.number > 1)

        return [self._row_to_ayah(r) for r in query.all()]

    def _row_to_ayah(self, row) -> Ayah:
        """Convert a SQLAlchemy Quran row to an Ayah dataclass."""
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
            first_position=None,
            last_position=None
        )
