import pytest
from core_functions.tasbih.controller import TasbihController


@pytest.fixture
def tasbih_controller(qapp, tmp_path):
    db_file = tmp_path / "tasbih.db"
    controller = TasbihController(str(db_file))
    yield controller
    controller.Session.remove()
    controller.engine.dispose()


class TestTasbihController:
    def test_default_entries_initialized(self, tasbih_controller):
        entries = tasbih_controller.get_all_entries()
        assert len(entries) == 6
        names = [e.name for e in entries]
        assert "سبحان الله" in names
        assert "الحمد لله" in names
        assert "الله أكبر" in names

    def test_add_entry_and_signal(self, tasbih_controller):
        added_entries = []
        tasbih_controller.entrieAdded.connect(added_entries.append)

        tasbih_controller.add_entry("سبحان الله وبحمده")
        entries = tasbih_controller.get_all_entries()
        assert len(entries) == 7
        assert len(added_entries) == 1
        assert added_entries[0].name == "سبحان الله وبحمده"

    def test_add_duplicate_entry_handled(self, tasbih_controller):
        initial_count = len(tasbih_controller.get_all_entries())
        # Duplicate name should be caught by IntegrityError and ignored
        tasbih_controller.add_entry("سبحان الله")
        assert len(tasbih_controller.get_all_entries()) == initial_count

    def test_counter_increment_decrement_clamping(self, tasbih_controller):
        entry = tasbih_controller.get_all_entries()[0]
        entry_id = entry.id
        assert entry.counter == 0

        # Increment
        tasbih_controller.increment_entry_counter(entry_id)
        updated = tasbih_controller.get_entry(entry_id)
        assert updated.counter == 1

        tasbih_controller.increment_entry_counter(entry_id)
        updated = tasbih_controller.get_entry(entry_id)
        assert updated.counter == 2

        # Decrement
        tasbih_controller.decrement_entry_counter(entry_id)
        updated = tasbih_controller.get_entry(entry_id)
        assert updated.counter == 1

        # Decrement to zero
        tasbih_controller.decrement_entry_counter(entry_id)
        updated = tasbih_controller.get_entry(entry_id)
        assert updated.counter == 0

        # Decrement below zero is clamped at 0
        tasbih_controller.decrement_entry_counter(entry_id)
        updated = tasbih_controller.get_entry(entry_id)
        assert updated.counter == 0

    def test_reset_single_counter(self, tasbih_controller):
        entry = tasbih_controller.get_all_entries()[0]
        tasbih_controller.increment_entry_counter(entry.id)
        tasbih_controller.increment_entry_counter(entry.id)
        assert tasbih_controller.get_entry(entry.id).counter == 2

        tasbih_controller.reset_entry_counter(entry.id)
        assert tasbih_controller.get_entry(entry.id).counter == 0

    def test_reset_all_counters(self, tasbih_controller):
        for entry in tasbih_controller.get_all_entries():
            tasbih_controller.increment_entry_counter(entry.id)

        # Confirm counters > 0
        assert all(e.counter > 0 for e in tasbih_controller.get_all_entries())

        tasbih_controller.reset_all_entries()
        assert all(e.counter == 0 for e in tasbih_controller.get_all_entries())

    def test_delete_entry(self, tasbih_controller):
        entries = tasbih_controller.get_all_entries()
        target_id = entries[0].id

        tasbih_controller.delete_entry(target_id)
        remaining = tasbih_controller.get_all_entries()
        assert len(remaining) == 5
        assert tasbih_controller.get_entry(target_id) is None

    def test_delete_all_entries_reinitializes_defaults(self, tasbih_controller):
        # Add custom entry
        tasbih_controller.add_entry("تسبيح خاص")
        assert len(tasbih_controller.get_all_entries()) == 7

        # delete_all_entries deletes all and reinitializes 6 default entries
        tasbih_controller.delete_all_entries()
        entries = tasbih_controller.get_all_entries()
        assert len(entries) == 6
        names = [e.name for e in entries]
        assert "تسبيح خاص" not in names
