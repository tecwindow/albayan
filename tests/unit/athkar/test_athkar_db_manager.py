import pytest
from core_functions.athkar.athkar_db_manager import AthkarDBManager


@pytest.fixture
def athkar_db_manager(tmp_path):
    db_file = tmp_path / "athkar.db"
    manager = AthkarDBManager(str(db_file))
    yield manager
    manager.engine.dispose()


class TestAthkarDBManager:
    def test_create_and_get_category(self, athkar_db_manager):
        cat_id = athkar_db_manager.create_category(
            name="أذكار الصباح",
            audio_path="/audio/morning",
            from_time="05:00",
            to_time="10:00",
            play_interval=15,
            audio_athkar_enabled=1,
            text_athkar_enabled=1,
        )
        assert cat_id is not None

        categories = athkar_db_manager.get_all_categories()
        assert len(categories) == 1
        cat = categories[0]
        assert cat.name == "أذكار الصباح"
        assert cat.from_time == "05:00"
        assert cat.play_interval == 15

    def test_update_category(self, athkar_db_manager):
        cat_id = athkar_db_manager.create_category(name="أذكار المساء")
        athkar_db_manager.update_category(cat_id, name="أذكار المساء المحدثة", play_interval=60)

        categories = athkar_db_manager.get_all_categories()
        assert categories[0].name == "أذكار المساء المحدثة"
        assert categories[0].play_interval == 60

    def test_delete_category(self, athkar_db_manager):
        cat_id = athkar_db_manager.create_category(name="للحذف")
        assert len(athkar_db_manager.get_all_categories()) == 1

        athkar_db_manager.delete_category(cat_id)
        assert len(athkar_db_manager.get_all_categories()) == 0

    def test_text_athkar_crud(self, athkar_db_manager):
        cat_id = athkar_db_manager.create_category(name="أذكار عامة")

        items = [
            {"name": "ذكر 1", "text": "سبحان الله"},
            {"name": "ذكر 2", "text": "الحمد لله"},
        ]
        athkar_db_manager.add_text_athkar(items, cat_id)

        text_items = athkar_db_manager.get_text_athkar(cat_id)
        assert len(text_items) == 2
        assert text_items[0].text == "سبحان الله"

        # Update
        item_id = text_items[0].id
        athkar_db_manager.update_text_athkar(item_id, text="سبحان الله العظيم")
        updated_items = athkar_db_manager.get_text_athkar(cat_id)
        assert updated_items[0].text == "سبحان الله العظيم"

        # Delete
        athkar_db_manager.delete_text_athkar(item_id)
        remaining = athkar_db_manager.get_text_athkar(cat_id)
        assert len(remaining) == 1
        assert remaining[0].name == "ذكر 2"

    def test_audio_athkar_crud(self, athkar_db_manager):
        cat_id = athkar_db_manager.create_category(name="أذكار صوتية")

        files = ["01.mp3", "02.mp3", "03.mp3"]
        athkar_db_manager.add_audio_athkar(files, cat_id)

        audio_items = athkar_db_manager.get_audio_athkar(cat_id)
        assert len(audio_items) == 3
        assert audio_items[0].audio_file_name == "01.mp3"

        # Update
        first_id = audio_items[0].id
        athkar_db_manager.update_audio_athkar(first_id, audio_file_name="01_updated.mp3")
        updated_items = athkar_db_manager.get_audio_athkar(cat_id)
        assert updated_items[0].audio_file_name == "01_updated.mp3"

        # Bulk delete
        ids_to_delete = [audio_items[1].id, audio_items[2].id]
        athkar_db_manager.delete_audio_athkar(ids_to_delete)
        remaining = athkar_db_manager.get_audio_athkar(cat_id)
        assert len(remaining) == 1
        assert remaining[0].id == first_id
