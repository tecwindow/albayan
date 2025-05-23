# -*- coding: utf-8 -*-

from typing import Optional, Dict
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from .models import AyahMapBase, AyahViewMap
from .types import Ayah, NavigationMode
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class ViewContent:
    def __init__(self, number: int, label: str, mode: NavigationMode, db_url: str = "sqlite:///:memory:"):
        logger.debug(f"Initializing ViewContent with number: {number}, label: {label}, mode: {mode}")
        self.number = number
        self.label = label
        self.mode = mode
        self.text = ""
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session: Session = self.Session()
        AyahMapBase.metadata.create_all(self.engine)
        logger.debug(f"Initialized ViewContent with number: {number}, label: {label}, mode: {mode}")

    @property
    def edit_label(self) -> str:
        if self.mode == NavigationMode.SURAH:
            return f"{self.label} {self.start_ayah.sura_name}"
        else:
            return f"ال{self.label} {self.number}"
        
    @property
    def start_ayah(self) -> Optional[Ayah]:
        ayah_row = (
            self.session.query(AyahViewMap)
            .order_by(AyahViewMap.first_position.asc())
            .first()
        )
        return self._row_to_ayah(ayah_row) if ayah_row else None

    @property
    def end_ayah(self) -> Optional[Ayah]:
        ayah_row = (
            self.session.query(AyahViewMap)
            .order_by(AyahViewMap.first_position.desc())
            .first()
        )
        return self._row_to_ayah(ayah_row) if ayah_row else None

    def insert(self, ayah: Ayah):
        ayah_row = AyahViewMap(
            number=ayah.number,
            text=ayah.text,
            sura_name=ayah.sura_name,
            sura_number=ayah.sura_number,
            number_in_surah=ayah.number_in_surah,
            juz=ayah.juz,
            hizb=ayah.hizb,
            hizbQuarter=ayah.hizbQuarter,
            page=ayah.page,
            first_position=ayah.first_position,
            last_position=ayah.last_position,
            sajda=ayah.sajda,
            sajdaObligation=ayah.sajdaObligation,
        )
        self.session.add(ayah_row)
        self.session.commit()

    def get_by_position(self, position: int) -> Optional[Ayah]:
        ayah_row = (
            self.session.query(AyahViewMap)
            .filter(AyahViewMap.first_position <= position, AyahViewMap.last_position >= position)
            .first()
        )
        return self._row_to_ayah(ayah_row) if ayah_row else None

    def get_by_ayah_number(self, ayah_number: int) -> Optional[Ayah]:
        ayah_row = (
            self.session.query(AyahViewMap)
            .filter(
                AyahViewMap.number== ayah_number
            )
            .first()
        )
        return self._row_to_ayah(ayah_row) if ayah_row else None

    def get_ayah_range(self) -> Dict[int, Dict[str, int]]:
        result = {}
        rows = (
            self.session.query(
                AyahViewMap.sura_number,
                func.min(AyahViewMap.number_in_surah).label("min_ayah"),
                func.max(AyahViewMap.number_in_surah).label("max_ayah"),
            )
            .group_by(AyahViewMap.sura_number)
            .all()
        )
        for row in rows:
            result[row.sura_number] = {"min_ayah": row.min_ayah, "max_ayah": row.max_ayah}
        return result

    def _row_to_ayah(self, row) -> Ayah:
        return Ayah(
            number=row.number,
            text=row.text,
            sura_name=row.sura_name,
            sura_number=row.sura_number,
            number_in_surah=row.number_in_surah,
            juz=row.juz,
            hizb=row.hizb,
            hizbQuarter=row.hizbQuarter,
            page=row.page,
            sajda=row.sajda,
            sajdaObligation=row.sajdaObligation,
            last_position=row.last_position,
            first_position=row.first_position,
        )

    def __repr__(self) -> str:
        return f"ViewContent(number={self.number}, label={self.label}, mode={self.mode})"
    