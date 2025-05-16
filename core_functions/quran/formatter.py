from typing import List
from .types import Ayah
from .view_content import ViewContent


class AyahFormatter:
    def __init__(self, show_ayah_number: bool = True, aya_to_line: bool = True, auto_page_turn: bool = False):
        self.show_ayah_number = show_ayah_number
        self.aya_to_line = aya_to_line
        self.auto_page_turn = auto_page_turn

    def format_view(self, ayat: List[Ayah], current_pos: int = 0) -> ViewContent:
        text = ""
        current_position = 0
        view_items = []

        for i, ayah in enumerate(ayat):
            ayah_text = ayah.text

            if ayah.number_in_surah == 1:
                start_point = f"{ayah.sura_name} {ayah.number_in_surah}\n|\n"
                ayah_text = start_point + ayah_text
                if ayah.number_in_surah != 1:
                    ayah_text = ayah_text.replace(
                        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ", 
                        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n"
                    )

            if self.show_ayah_number:
                ayah_text += f" ({ayah.number_in_surah})"

            ayah_text = f"{ayah_text}\n" if self.aya_to_line else f"{ayah_text} "

            if i == 0 and current_pos != 1:
                ayah_text = f"|\n{ayah_text}"

            # تحديد المواضع
            first_position = current_position
            current_position += len(ayah_text)
            last_position = current_position - 1

            # تحديث نص العرض
            text += ayah_text

            # بناء العنصر الجديد
            view_items.append(Ayah(
                number=ayah.number,
                text=ayah.text,
                sura_name=ayah.sura_name,
                sura_number=ayah.sura_number,
                number_in_surah=ayah.number_in_surah,
                juz=ayah.juz,
                hizb=ayah.hizb,
                hizbQuarter=ayah.hizbQuarter,
                page=ayah.page,
                first_position=first_position,
                last_position=last_position,
                sajda=ayah.sajda,
                sajdaObligation=ayah.sajdaObligation
            ))

        if auto_page_turn:
            text += "|"
        else:
            text = text.strip()

        return ViewContent(text=text, ayat=view_items)
