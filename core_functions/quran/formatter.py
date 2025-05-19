from typing import List
from .types import Ayah
from .view_content import ViewContent
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class AyahFormatter:
    def __init__(self, view_content: ViewContent, show_ayah_number: bool = True, auto_page_turn: bool = False):
        logger.debug("Initializing AyahFormatter")
        self.view_content = view_content
        self.show_ayah_number = show_ayah_number
        self.auto_page_turn = auto_page_turn
        logger.debug(f"Initialized AyahFormatter with view_content: {view_content}, show_ayah_number: {show_ayah_number}, auto_page_turn: {auto_page_turn}")

    def format_view(self, ayat: List[Ayah]) -> ViewContent:
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

            if self.show_ayah_number:
                ayah_text += f" ({ayah.number_in_surah})"

            ayah_text = f"{ayah_text}\n"
            ayah_text = f"|\n{ayah_text}" if i == 0 and self.view_content.number != 1 else ayah_text                
            text += ayah_text

            # Calculate the positions
            ayah.first_position = current_position
            current_position += len(ayah_text)
            ayah.last_position = current_position - 1
            self.view_content.insert(ayah)

        if self.auto_page_turn:
            text += "|"
        else:
            text = text.strip()

        self.view_content.text = text
        
        return self.view_content

    def __repr__(self) -> str:
        return f"AyahFormatter(view_content={self.view_content}, show_ayah_number={self.show_ayah_number}, auto_page_turn={self.auto_page_turn})"
