# -*- coding: utf-8 -*-

from typing import List
from pydantic import BaseModel
from .types import Ayah
from .view_content import ViewContent
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class FomatterOptions(BaseModel):
    """
    Formatter options for the Quran text.
    """
    show_ayah_number: bool = True
    auto_page_turn: bool = False


class QuranFormatter:
    def __init__(self, view_content: ViewContent, formatter_options: FomatterOptions):
        """
        Initialize the AyahFormatter with view content and formatting options.

        args:
     view_content (ViewContent): The view content obj.
     formatter_options (FomatterOptions): The formatter options obj.
        """
        logger.debug("Initializing AyahFormatter")
        self.view_content = view_content
        self.formatter_options = formatter_options
        logger.debug(f"Initialized AyahFormatter with view_content: {view_content}, formatter_options: {formatter_options}")

    def format_view(self, ayat: List[Ayah]) -> ViewContent:
        """Format the view content with ayat text and positions."""
        text = ""
        current_position = 0

        for i, ayah in enumerate(ayat):
            ayah_text = ayah.text

            if ayah.number_in_surah == 1:
                start_point = f"{ayah.sura_name} {ayah.number_in_surah}\n|\n"
                ayah_text = start_point + ayah_text
                if ayah.sura_number != 1:
                    ayah_text = ayah_text.replace(
                        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ", 
                        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n"
                    )

            if self.formatter_options.show_ayah_number:
                ayah_text += f" ({ayah.number_in_surah})"

            ayah_text = f"{ayah_text}\n"
            ayah_text = f"|\n{ayah_text}" if i == 0 and self.view_content.number != 1 else ayah_text                
            text += ayah_text

            # Calculate the positions
            ayah.first_position = current_position
            current_position += len(ayah_text)
            ayah.last_position = current_position - 1
            self.view_content.insert(ayah)

        if self.formatter_options.auto_page_turn:
            text += "|"
        else:
            text = text.strip()

        self.view_content.text = text
        
        return self.view_content

    def __repr__(self) -> str:
        return f"QuranFormatter(view_content={self.view_content}, formatter_options={self.formatter_options})"
