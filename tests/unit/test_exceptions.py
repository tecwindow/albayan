import pytest
from unittest.mock import MagicMock
from exceptions.base import BaseException, ErrorMessage
from exceptions.database import (
    DBNotFoundError,
    InvalidCriteriaError,
    DatabaseConnectionError,
    InvalidSearchTextError,
)
from exceptions.json import (
    JSONFileNotFoundError,
    InvalidJSONFormatError,
    MissingKeyError,
)


class DummyException(BaseException):
    pass


class TestBaseException:
    def test_default_values(self):
        exc = DummyException()
        assert exc.message == "An error occurred"
        assert exc.cause is None
        assert exc.code == 0
        assert str(exc) == "[Error Code: 0] An error occurred"

    def test_custom_values_without_cause(self):
        exc = DummyException("Custom message", None, 42)
        assert exc.message == "Custom message"
        assert exc.cause is None
        assert exc.code == 42
        assert str(exc) == "[Error Code: 42] Custom message"

    def test_with_cause(self):
        underlying = ValueError("Bad value")
        exc = DummyException("Failed operation", underlying, 99)
        assert exc.cause is underlying
        assert "[Error Code: 99] Failed operation" in str(exc)
        assert "ValueError('Bad value')" in str(exc)


class TestErrorMessage:
    def test_error_message_with_custom_exception(self, monkeypatch):
        from utils.const import Globals
        mock_effects = MagicMock()
        monkeypatch.setattr(Globals, "effects_manager", mock_effects)

        exc = DummyException("Something broke", None, 123)
        err = ErrorMessage(exc)

        assert err.get_code() == 123
        assert err.title == "خطأ"

        body = err.body
        mock_effects.play.assert_called_once_with("error")
        assert "رمز الخطأ: 123" in body

        log_msg = err.log_message
        assert "Error Type: DummyException" in log_msg
        assert "Code: 123" in log_msg
        assert str(err) == log_msg

    def test_error_message_with_standard_exception(self, monkeypatch):
        from utils.const import Globals
        mock_effects = MagicMock()
        monkeypatch.setattr(Globals, "effects_manager", mock_effects)

        exc = RuntimeError("Standard Python exception")
        err = ErrorMessage(exc)

        assert err.get_code() is None
        body = err.body
        assert "\nرمز الخطأ:" not in body

        log_msg = err.log_message
        assert "Error Type: RuntimeError" in log_msg
        assert "Code: N/A" in log_msg


class TestDatabaseExceptions:
    def test_db_not_found_error(self):
        exc = DBNotFoundError("/path/to/missing.db")
        assert exc.code == 101
        assert "/path/to/missing.db" in str(exc)

    def test_invalid_criteria_error(self):
        exc = InvalidCriteriaError("bad_criteria")
        assert exc.code == 102
        assert "bad_criteria" in str(exc)

    def test_database_connection_error(self):
        cause = OSError("Disk error")
        exc = DatabaseConnectionError("timeout", cause=cause)
        assert exc.code == 103
        assert "timeout" in str(exc)
        assert exc.cause is cause

    def test_invalid_search_text_error(self):
        exc = InvalidSearchTextError("   ")
        assert exc.code == 104
        assert "   " in str(exc)


class TestJSONExceptions:
    def test_json_file_not_found(self):
        exc = JSONFileNotFoundError("config.json")
        assert exc.code == 200
        assert "config.json" in str(exc)

    def test_invalid_json_format(self):
        cause = ValueError("Expecting value")
        exc = InvalidJSONFormatError("data.json", cause=cause)
        assert exc.code == 201
        assert "data.json" in str(exc)
        assert exc.cause is cause

    def test_missing_key_error(self):
        exc = MissingKeyError("api_key", "secrets.json")
        assert exc.code == 202
        assert "api_key" in str(exc)
        assert "secrets.json" in str(exc)
