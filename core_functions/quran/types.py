# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from pathlib import Path
from utils.const import data_folder


class NavigationMode(Enum):
    PAGE = 0
    SURAH = 1
    QUARTER = 2
    HIZB = 3
    JUZ = 4
    CUSTOM_RANGE = 5

    @staticmethod
    def from_int(value: int) -> "NavigationMode":
        return NavigationMode(value)
    
    
class QuranFontType(Enum):
    DEFAULT = 0
    UTHMANI = 1

    @staticmethod
    def from_int(value: int) -> "QuranFontType":
        return QuranFontType(value)
 
    @property
    def database(self) -> Path:
        paths = {
            QuranFontType.DEFAULT: data_folder / "quran" / "quran.DB",
            QuranFontType.UTHMANI: data_folder / "quran" / "uthmani.DB",
        }
        return paths[self] 
 

@dataclass(eq=True)
class Surah:
    number: int
    name: str
    ayah_count: int
    first_ayah_number: int
    last_ayah_number: int

    
@dataclass(eq=True)
class Ayah:
    number: int
    text: str
    sura_name: str
    sura_number: int
    number_in_surah: int
    juz: int
    hizb: int
    hizbQuarter: int
    page: int
    sajda: bool
    sajdaObligation: bool
    first_position: Optional[int] = None
    last_position: Optional[int] = None
