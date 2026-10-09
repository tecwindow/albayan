import pytest
from unittest.mock import MagicMock
from core_functions.quran.formatter import QuranFormatter, FormatterOptions
from core_functions.quran.types import MarksType, Ayah


@pytest.fixture
def sample_ayah():
    return Ayah(
        number=1,
        text="بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
        sura_name="الفاتحة",
        sura_number=1,
        number_in_surah=1,
        juz=1,
        hizb=1,
        hizbQuarter=1,
        page=1,
        sajda=False,
        sajdaObligation=False,
    )


@pytest.fixture
def mock_view_content():
    view = MagicMock()
    view.number = 1
    view.text = ""
    return view


class TestQuranFormatter:
    def test_convert_english_to_arabic_number(self):
        assert QuranFormatter.convert_english_to_arabic_number(0) == "٠"
        assert QuranFormatter.convert_english_to_arabic_number(123) == "١٢٣"
        assert QuranFormatter.convert_english_to_arabic_number(789) == "٧٨٩"
        assert QuranFormatter.convert_english_to_arabic_number(604) == "٦٠٤"

    def test_replace_marks_text_mode(self, mock_view_content):
        options = FormatterOptions(marks_type=MarksType.TEXT)
        formatter = QuranFormatter(mock_view_content, options)

        raw_text = "آية ۩ وقف ۚ وقف آخر ۗ و ۖ و ۘ و ۙ و ۛ و ۜ"
        replaced = formatter.replace_marks(raw_text)

        assert "(سجدة)" in replaced
        assert "(ج)" in replaced
        assert "(قلى)" in replaced
        assert "(صلى)" in replaced
        assert "(م)" in replaced
        assert "(لا)" in replaced
        assert "--" in replaced
        assert "س" in replaced

    def test_replace_marks_accessible_mode(self, mock_view_content):
        options = FormatterOptions(marks_type=MarksType.ACCESSIBLE)
        formatter = QuranFormatter(mock_view_content, options)

        raw_text = "آية ۩ وقف ۚ وقف آخر ۗ و ۖ و ۘ"
        replaced = formatter.replace_marks(raw_text)

        assert "(سجدة)" in replaced
        assert "(،)" in replaced
        assert "(.ء)" in replaced
        assert "(؛)" in replaced
        assert "(.)" in replaced

    def test_format_view_surah_header_and_positions(self, mock_view_content, sample_ayah):
        options = FormatterOptions(show_ayah_number=True, auto_page_turn=False, marks_type=MarksType.DEFAULT)
        formatter = QuranFormatter(mock_view_content, options)

        ayah2 = Ayah(
            number=2,
            text="ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ",
            sura_name="الفاتحة",
            sura_number=1,
            number_in_surah=2,
            juz=1,
            hizb=1,
            hizbQuarter=1,
            page=1,
            sajda=False,
            sajdaObligation=False,
        )

        formatted_text = formatter.format_view([sample_ayah, ayah2])

        # Header appears for ayah 1
        assert "الفاتحة (١)\n|\n" in formatted_text
        # Ayah numbers in Arabic digits
        assert "(١)" in formatted_text
        assert "(٢)" in formatted_text
        # Position mapping
        assert sample_ayah.first_position == 0
        assert sample_ayah.last_position > sample_ayah.first_position
        assert ayah2.first_position == sample_ayah.last_position + 1
        assert ayah2.last_position > ayah2.first_position

        # Bulk insert called on view_content
        mock_view_content.insert_bulk.assert_called_once()
        assert mock_view_content.text == formatted_text

    def test_format_view_without_ayah_numbers(self, mock_view_content, sample_ayah):
        options = FormatterOptions(show_ayah_number=False, auto_page_turn=False)
        formatter = QuranFormatter(mock_view_content, options)

        formatted_text = formatter.format_view([sample_ayah])
        # Ayah number in surah should NOT be appended at the end of the ayah line
        # Header has sura_number (١), but ayah itself shouldn't have trailing (١)
        assert not formatted_text.endswith("(١)")

    def test_format_view_with_auto_page_turn(self, mock_view_content, sample_ayah):
        options = FormatterOptions(auto_page_turn=True)
        formatter = QuranFormatter(mock_view_content, options)

        formatted_text = formatter.format_view([sample_ayah])
        assert formatted_text.endswith("|")

    def test_format_view_basmalah_separation_for_non_fatiha(self, mock_view_content):
        # Surah 2 (Al-Baqarah), Ayah 1 has Basmalah
        baqarah_ayah1 = Ayah(
            number=8,
            text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الم",
            sura_name="البقرة",
            sura_number=2,
            number_in_surah=1,
            juz=1,
            hizb=1,
            hizbQuarter=1,
            page=2,
            sajda=False,
            sajdaObligation=False,
        )
        options = FormatterOptions(show_ayah_number=True)
        formatter = QuranFormatter(mock_view_content, options)

        formatted_text = formatter.format_view([baqarah_ayah1])
        assert "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\nالم" in formatted_text
