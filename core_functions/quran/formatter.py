# -*- coding: utf-8 -*-

import re
from typing import List
from pydantic import BaseModel
from .types import MarksType, Ayah
from .view_content import ViewContent
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class FormatterOptions(BaseModel):
    """
    Formatter options for the Quran text.
    """
    show_ayah_number: bool = True
    auto_page_turn: bool = False
    marks_type: MarksType = MarksType.DEFAULT


class QuranFormatter:
    def __init__(self, view_content: ViewContent, formatter_options: FormatterOptions):
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

    def replace_marks(self, text: str) -> str:
        """
        Replace the marks in the text with accessible marks.

        args:
            text (str): The text to replace marks in.

        returns:
            str: The text with replaced marks.
        """
        
        if self.formatter_options.marks_type == MarksType.TEXT:
            marks = {
                "۩": "(سجدة)",
                "ۚ": "(ج)",
                "ۗ": "(قلى)",
                "ۖ": "(صلى)",
                "ۘ": "(م)",
                "ۙ": "(لا)",
                "ۛ": "--",
                "ۜ": "س"
            }
        elif self.formatter_options.marks_type == MarksType.ACCESSIBLE:
            marks = {
                "۩": "(سجدة)",
                "ۚ": "(،)",
                "ۗ": "(ء)",
                "ۖ": "(;)",
                "ۘ": "(.)",
                "ۙ": "(لا)",
                "ۛ": "--",
                "ۜ": "س"
            }

        for mark, replacement in marks.items():
            text = text.replace(mark, replacement)
    
        return text
    
    @staticmethod
    def convert_english_to_arabic_number(english_number: int) -> str:
        """
        Converts English digits in a string to Arabic-Indic digits.

        Args:
            english_number (str): A string containing English digits (e.g., "123").

        Returns:
            str: A string with Arabic digits (e.g., "١٢٣").
        """
        english_to_arabic = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
        return str(english_number).translate(english_to_arabic)

    def format_view(self, ayahs: List[Ayah]) -> str:
        """Format the view content with ayat text and positions."""
        text = ""
        current_position = 0
        final_ayahs = []

        for i, ayah in enumerate(ayahs):
            ayah_text = ayah.text
            if self.formatter_options.marks_type != MarksType.DEFAULT:
                ayah_text = self.replace_marks(ayah_text)

            if ayah.number_in_surah == 1:
                start_point = f"{ayah.sura_name} ({self.convert_english_to_arabic_number(ayah.sura_number)})\n|\n"
                ayah_text = start_point + ayah_text
                if ayah.sura_number != 1:
                    ayah_text = ayah_text.replace(
                        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ", 
                        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n"
                    )

            if self.formatter_options.show_ayah_number:
                ayah_text += f" ({self.convert_english_to_arabic_number(ayah.number_in_surah)})"

            ayah_text = f"{ayah_text}\n"
            ayah_text = f"|\n{ayah_text}" if i == 0 and self.view_content.number != 1 else ayah_text                
            text += ayah_text

            # Calculate the positions
            ayah.first_position = current_position
            current_position += len(ayah_text)
            ayah.last_position = current_position - 1
            final_ayahs.append(ayah)

        if self.formatter_options.auto_page_turn:
            text += "|"
        else:
            text = text.strip()

        self.view_content.text = text
        self.view_content.insert_bulk(final_ayahs)
        
        return text

    def __repr__(self) -> str:
        return f"QuranFormatter(view_content={self.view_content}, formatter_options={self.formatter_options})"
