import pytest
from core_functions.quran.view_content import ViewContent
from core_functions.quran.types import NavigationMode, Ayah


@pytest.fixture
def sample_ayahs():
    a1 = Ayah(
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
        first_position=0,
        last_position=38,
    )
    a2 = Ayah(
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
        first_position=39,
        last_position=75,
    )
    a3 = Ayah(
        number=8,
        text="الم",
        sura_name="البقرة",
        sura_number=2,
        number_in_surah=1,
        juz=1,
        hizb=1,
        hizbQuarter=1,
        page=2,
        sajda=False,
        sajdaObligation=False,
        first_position=76,
        last_position=90,
    )
    return [a1, a2, a3]


class TestViewContent:
    def test_insert_and_start_end_ayah(self, sample_ayahs):
        vc = ViewContent(number=1, label="صفحة", mode=NavigationMode.PAGE)
        vc.insert(sample_ayahs[0])
        vc.insert(sample_ayahs[1])

        assert vc.start_ayah.number == 1
        assert vc.end_ayah.number == 2

    def test_insert_bulk(self, sample_ayahs):
        vc = ViewContent(number=1, label="صفحة", mode=NavigationMode.PAGE)
        vc.insert_bulk(sample_ayahs)

        assert vc.start_ayah.number == 1
        assert vc.end_ayah.number == 8

    def test_edit_label_formatting(self, sample_ayahs):
        # PAGE mode -> "الصفحة 1"
        vc_page = ViewContent(number=1, label="صفحة", mode=NavigationMode.PAGE)
        vc_page.insert_bulk(sample_ayahs[:2])
        assert vc_page.edit_label == "الصفحة 1"

        # SURAH mode -> sura_name
        vc_surah = ViewContent(number=1, label="سورة", mode=NavigationMode.SURAH)
        vc_surah.insert_bulk(sample_ayahs[:2])
        assert vc_surah.edit_label == "الفاتحة"

        # CUSTOM_RANGE mode -> "آية ... / آية ..."
        vc_range = ViewContent(number=1, label="نطاق", mode=NavigationMode.CUSTOM_RANGE)
        vc_range.insert_bulk(sample_ayahs)
        assert "آية 1 الفاتحة" in vc_range.edit_label
        assert "آية 1 البقرة" in vc_range.edit_label

    def test_get_by_position(self, sample_ayahs):
        vc = ViewContent(number=1, label="صفحة", mode=NavigationMode.PAGE)
        vc.insert_bulk(sample_ayahs)

        # Position 20 falls inside Ayah 1 (0 to 38)
        found_a1 = vc.get_by_position(20)
        assert found_a1.number == 1

        # Position 50 falls inside Ayah 2 (39 to 75)
        found_a2 = vc.get_by_position(50)
        assert found_a2.number == 2

    def test_get_by_ayah_number(self, sample_ayahs):
        vc = ViewContent(number=1, label="صفحة", mode=NavigationMode.PAGE)
        vc.insert_bulk(sample_ayahs)

        found = vc.get_by_ayah_number(2)
        assert found.number == 2
        assert found.number_in_surah == 2

        # Nonexistent falls back to start_ayah
        fallback = vc.get_by_ayah_number(999)
        assert fallback.number == 1

    def test_get_by_ayah_number_in_surah(self, sample_ayahs):
        vc = ViewContent(number=1, label="صفحة", mode=NavigationMode.PAGE)
        vc.insert_bulk(sample_ayahs)

        # Surah 1, Ayah 2
        found = vc.get_by_ayah_number_in_surah(ayah_number_in_surah=2, surah_number=1)
        assert found is not None
        assert found.number == 2

        # Nonexistent returns None
        not_found = vc.get_by_ayah_number_in_surah(ayah_number_in_surah=99, surah_number=1)
        assert not_found is None

    def test_get_ayah_range(self, sample_ayahs):
        vc = ViewContent(number=1, label="صفحة", mode=NavigationMode.PAGE)
        vc.insert_bulk(sample_ayahs)

        ranges = vc.get_ayah_range()
        assert 1 in ranges
        assert ranges[1]["surah_name"] == "الفاتحة"
        assert ranges[1]["min_ayah"] == 1
        assert ranges[1]["max_ayah"] == 2

        assert 2 in ranges
        assert ranges[2]["surah_name"] == "البقرة"
        assert ranges[2]["min_ayah"] == 1
        assert ranges[2]["max_ayah"] == 1
