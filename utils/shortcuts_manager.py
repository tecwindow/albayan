"""
Shortcuts Manager for Albayan.
Manages loading, saving, conflict detection, and applying customizable keyboard shortcuts.
Provides fallback to built-in defaults if user configuration is missing or corrupted.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from utils.paths import paths
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

# Complete built-in default shortcuts dictionary.
# Preserved in code as source of truth and fallback.
DEFAULT_SHORTCUTS: Dict[str, dict] = {
    # --- Navigation ---
    "next_action": {
        "label": "التالي",
        "shortcuts": ["Ctrl+N", "Ctrl+Down", "Alt+Right", "PgDown"],
        "category": "التنقل",
    },
    "previous_action": {
        "label": "السابق",
        "shortcuts": ["Ctrl+B", "PgUp", "Ctrl+Up", "Alt+Left"],
        "category": "التنقل",
    },
    "go_to_saved_position_action": {
        "label": "الذهاب إلى الموضع المحفوظ",
        "shortcuts": ["Ctrl+Backspace"],
        "category": "التنقل",
    },
    "search_action": {
        "label": "البحث",
        "shortcuts": ["Ctrl+F"],
        "category": "التنقل",
    },
    "go_to_action": {
        "label": "اذهب إلى",
        "shortcuts": ["Ctrl+G"],
        "category": "التنقل",
    },
    "go_to_ayah_action": {
        "label": "الذهاب إلى آية",
        "shortcuts": ["Shift+G"],
        "category": "التنقل",
    },
    "quick_access_action": {
        "label": "الوصول السريع",
        "shortcuts": ["Ctrl+Q"],
        "category": "التنقل",
    },
    "close_action": {
        "label": "إغلاق النافذة",
        "shortcuts": ["Ctrl+W", "Ctrl+F4"],
        "category": "التنقل",
    },
    "exit_action": {
        "label": "إغلاق البرنامج",
        "shortcuts": ["Ctrl+Shift+W", "Ctrl+Shift+F4"],
        "category": "التنقل",
    },
    # --- Browse Mode ---
    "browse_mode_surah": {
        "label": "وضع السور",
        "shortcuts": ["Ctrl+1"],
        "category": "وضع التصفح",
    },
    "browse_mode_page": {
        "label": "وضع الصفحات",
        "shortcuts": ["Ctrl+2"],
        "category": "وضع التصفح",
    },
    "browse_mode_quarter": {
        "label": "وضع الأرباع",
        "shortcuts": ["Ctrl+3"],
        "category": "وضع التصفح",
    },
    "browse_mode_hizb": {
        "label": "وضع الأحزاب",
        "shortcuts": ["Ctrl+4"],
        "category": "وضع التصفح",
    },
    "browse_mode_juz": {
        "label": "وضع الأجزاء",
        "shortcuts": ["Ctrl+5"],
        "category": "وضع التصفح",
    },
    "browse_mode_custom": {
        "label": "وضع مخصص",
        "shortcuts": ["Ctrl+6"],
        "category": "وضع التصفح",
    },
    # --- Playback ---
    "play_pause_action": {
        "label": "تشغيل/إيقاف مؤقت",
        "shortcuts": ["K", "Ctrl+P"],
        "category": "المشغل",
    },
    "stop_action": {
        "label": "إيقاف",
        "shortcuts": ["Ctrl+E"],
        "category": "المشغل",
    },
    "rewind_action": {
        "label": "ترجيع",
        "shortcuts": ["J", "Ctrl+Alt+Left"],
        "category": "المشغل",
    },
    "forward_action": {
        "label": "تقديم",
        "shortcuts": ["L", "Ctrl+Alt+Right"],
        "category": "المشغل",
    },
    "replay_action": {
        "label": "إعادة",
        "shortcuts": ["Shift+J"],
        "category": "المشغل",
    },
    "play_next_action": {
        "label": "تشغيل الآية التالية",
        "shortcuts": ["Ctrl+Shift+N"],
        "category": "المشغل",
    },
    "play_previous_action": {
        "label": "تشغيل الآية السابقة",
        "shortcuts": ["Ctrl+Shift+B"],
        "category": "المشغل",
    },
    # --- Quick Keys (QuranInterface shortcuts) ---
    "focus_quran_view": {
        "label": "التركيز على نص القرآن",
        "shortcuts": ["Ctrl+M"],
        "category": "مفاتيح سريعة",
    },
    "say_played_ayah": {
        "label": "قراءة الآية المشغلة",
        "shortcuts": ["C"],
        "category": "مفاتيح سريعة",
    },
    "say_repeat_ayah": {
        "label": "قراءة حالة التكرار",
        "shortcuts": ["B"],
        "category": "مفاتيح سريعة",
    },
    "change_ayah_focus": {
        "label": "تغيير التركيز على الآية",
        "shortcuts": ["Alt+Shift+C"],
        "category": "مفاتيح سريعة",
    },
    "say_focused_ayah": {
        "label": "قراءة الآية المحددة",
        "shortcuts": ["V"],
        "category": "مفاتيح سريعة",
    },
    # --- Actions ---
    "save_position_action": {
        "label": "حفظ الموضع الحالي",
        "shortcuts": ["Ctrl+S"],
        "category": "الإجراءات",
    },
    "save_bookmark_action": {
        "label": "حفظ علامة",
        "shortcuts": ["Ctrl+D"],
        "category": "الإجراءات",
    },
    "verse_tafsir_action": {
        "label": "تفسير الآية",
        "shortcuts": ["Ctrl+T"],
        "category": "الإجراءات",
    },
    "tafaseer_menu_action": {
        "label": "قائمة التفسير",
        "shortcuts": ["Shift+T"],
        "category": "الإجراءات",
    },
    "verse_info_action": {
        "label": "أسباب نزول الآية",
        "shortcuts": ["Shift+R"],
        "category": "الإجراءات",
    },
    "verse_grammar_action": {
        "label": "إعراب الآية",
        "shortcuts": ["Shift+E"],
        "category": "الإجراءات",
    },
    "copy_verse_action": {
        "label": "نسخ الآية",
        "shortcuts": ["Shift+C"],
        "category": "الإجراءات",
    },
    # --- Info ---
    "ayah_info_action": {
        "label": "معلومات الآية",
        "shortcuts": ["Shift+I", "Alt+Shift+7"],
        "category": "المعلومات",
    },
    "surah_info_action": {
        "label": "معلومات السورة",
        "shortcuts": ["Alt+Shift+1", "Ctrl+I"],
        "category": "المعلومات",
    },
    "page_info_action": {
        "label": "معلومات الصفحة",
        "shortcuts": ["Alt+Shift+2"],
        "category": "المعلومات",
    },
    "quarter_info_action": {
        "label": "معلومات الربع",
        "shortcuts": ["Alt+Shift+3"],
        "category": "المعلومات",
    },
    "hizb_info_action": {
        "label": "معلومات الحزب",
        "shortcuts": ["Alt+Shift+4"],
        "category": "المعلومات",
    },
    "juz_info_action": {
        "label": "معلومات الجزء",
        "shortcuts": ["Alt+Shift+5"],
        "category": "المعلومات",
    },
    "moshaf_info_action": {
        "label": "معلومات المصحف",
        "shortcuts": ["Alt+Shift+6"],
        "category": "المعلومات",
    },
    # --- Tools ---
    "sura_player_action": {
        "label": "مشغل سور القرآن",
        "shortcuts": ["Shift+P"],
        "category": "الأدوات",
    },
    "athkar_action": {
        "label": "الأذكار",
        "shortcuts": ["Shift+A"],
        "category": "الأدوات",
    },
    "bookmark_manager_action": {
        "label": "مدير العلامات",
        "shortcuts": ["Shift+D"],
        "category": "الأدوات",
    },
    "tasbih_action": {
        "label": "المسبحة",
        "shortcuts": ["Shift+S"],
        "category": "الأدوات",
    },
    "download_manager_action": {
        "label": "مدير التنزيلات",
        "shortcuts": ["Ctrl+J"],
        "category": "الأدوات",
    },
    "message_for_you_action": {
        "label": "رسالة لك",
        "shortcuts": ["Shift+M"],
        "category": "الأدوات",
    },
    # --- Preferences ---
    "settings_action": {
        "label": "الإعدادات",
        "shortcuts": ["Alt+S", "F3"],
        "category": "التفضيلات",
    },
    "change_reciter_action": {
        "label": "تغيير القارئ",
        "shortcuts": ["Ctrl+Shift+R"],
        "category": "التفضيلات",
    },
    "change_after_listening_action": {
        "label": "تغيير الإجراء بعد الاستماع",
        "shortcuts": ["Ctrl+Shift+U"],
        "category": "التفضيلات",
    },
    "change_repeat_limit_action": {
        "label": "تغيير عدد مرات تكرار الآية",
        "shortcuts": ["Ctrl+Shift+Y"],
        "category": "التفضيلات",
    },
    "change_text_repeat_action": {
        "label": "تغيير عدد مرات تكرار النص",
        "shortcuts": ["Ctrl+Shift+T"],
        "category": "التفضيلات",
    },
    "change_after_text_action": {
        "label": "تغيير الإجراء بعد النص",
        "shortcuts": ["Ctrl+Shift+E"],
        "category": "التفضيلات",
    },
    # --- Help ---
    "user_guide_action": {
        "label": "دليل البرنامج",
        "shortcuts": ["F1"],
        "category": "المساعدة",
    },
    "whats_new_action": {
        "label": "المستجدات",
        "shortcuts": ["F2"],
        "category": "المساعدة",
    },
    "shortcuts_action": {
        "label": "اختصارات لوحة المفاتيح",
        "shortcuts": ["Shift+F1"],
        "category": "المساعدة",
    },
    "marks_action": {
        "label": "علامات الوقف",
        "shortcuts": ["Shift+F2"],
        "category": "المساعدة",
    },
    "update_program_action": {
        "label": "تحديث البرنامج",
        "shortcuts": ["Ctrl+F2"],
        "category": "المساعدة",
    },
    "open_log_action": {
        "label": "فتح ملف السجل",
        "shortcuts": ["Shift+L"],
        "category": "المساعدة",
    },
    "about_program_action": {
        "label": "حول البرنامج",
        "shortcuts": ["Ctrl+F1"],
        "category": "المساعدة",
    },
}

CATEGORY_ORDER = [
    "التنقل",
    "وضع التصفح",
    "المشغل",
    "مفاتيح سريعة",
    "الإجراءات",
    "المعلومات",
    "الأدوات",
    "التفضيلات",
    "المساعدة",
]


class ShortcutsManager:
    """
    Manages custom keyboard shortcuts for Albayan.
    Loads and saves shortcuts from/to shortcuts.json in user's app folder.
    Falls back gracefully to DEFAULT_SHORTCUTS on any corruption or missing file.
    """

    _shortcuts_file: Optional[Path] = None
    _current_shortcuts: Dict[str, List[str]] = {}

    @classmethod
    def _get_file(cls) -> Path:
        if cls._shortcuts_file is None:
            cls._shortcuts_file = paths.app_folder / "shortcuts.json"
        return cls._shortcuts_file

    @classmethod
    def load(cls) -> None:
        """
        Load shortcuts from JSON file.
        If file does not exist, or is corrupted, fall back to defaults safely.
        """
        file = cls._get_file()
        cls._current_shortcuts = {}

        if not file.exists():
            cls._reset_to_defaults()
            logger.info("No custom shortcuts file found. Loaded built-in defaults.")
            return

        try:
            with open(file, "r", encoding="utf-8") as f:
                saved = json.load(f)

            if not isinstance(saved, dict):
                raise ValueError("Shortcuts JSON root must be a dictionary.")

            for action_id, info in DEFAULT_SHORTCUTS.items():
                if action_id in saved:
                    val = saved[action_id]
                    if isinstance(val, list):
                        # Filter to valid string entries
                        cls._current_shortcuts[action_id] = [
                            str(s).strip() for s in val if str(s).strip()
                        ]
                    else:
                        cls._current_shortcuts[action_id] = list(info["shortcuts"])
                else:
                    cls._current_shortcuts[action_id] = list(info["shortcuts"])

            logger.info(f"Shortcuts successfully loaded from {file}.")
        except Exception as e:
            logger.error(f"Error loading shortcuts from {file}: {e}. Falling back to defaults.", exc_info=True)
            cls._reset_to_defaults()

    @classmethod
    def save(cls) -> bool:
        """
        Save current shortcuts to JSON file.
        Returns True on success, False on error.
        """
        file = cls._get_file()
        try:
            file.parent.mkdir(parents=True, exist_ok=True)
            with open(file, "w", encoding="utf-8") as f:
                json.dump(cls._current_shortcuts, f, ensure_ascii=False, indent=2)
            logger.info(f"Shortcuts saved to {file}.")
            return True
        except Exception as e:
            logger.error(f"Error saving shortcuts to {file}: {e}", exc_info=True)
            return False

    @classmethod
    def _reset_to_defaults(cls) -> None:
        """Reset internal shortcuts state to defaults without saving."""
        cls._current_shortcuts = {
            action_id: list(info["shortcuts"])
            for action_id, info in DEFAULT_SHORTCUTS.items()
        }

    @classmethod
    def get(cls, action_id: str) -> List[str]:
        """Return the current list of shortcuts for an action (empty list means disabled)."""
        if not cls._current_shortcuts:
            cls.load()
        if action_id in cls._current_shortcuts:
            return list(cls._current_shortcuts[action_id])
        return list(DEFAULT_SHORTCUTS.get(action_id, {}).get("shortcuts", []))

    @classmethod
    def get_default(cls, action_id: str) -> List[str]:
        """Return the built-in default shortcuts for an action."""
        return list(DEFAULT_SHORTCUTS.get(action_id, {}).get("shortcuts", []))

    @classmethod
    def set(cls, action_id: str, shortcuts: List[str]) -> bool:
        """Set the shortcuts list for an action and persist."""
        if not cls._current_shortcuts:
            cls.load()
        # Clean shortcuts list (remove duplicates and empty strings)
        cleaned: List[str] = []
        for s in shortcuts:
            s_clean = s.strip()
            if s_clean and s_clean not in cleaned:
                cleaned.append(s_clean)
        cls._current_shortcuts[action_id] = cleaned
        return cls.save()

    @classmethod
    def add_shortcut(cls, action_id: str, shortcut: str) -> bool:
        """Add a single shortcut to an action if not already present."""
        shortcut = shortcut.strip()
        if not shortcut:
            return False
        current = cls.get(action_id)
        if shortcut not in current:
            current.append(shortcut)
            return cls.set(action_id, current)
        return True

    @classmethod
    def remove_shortcut(cls, action_id: str, shortcut: str) -> bool:
        """Remove a single shortcut from an action."""
        shortcut = shortcut.strip()
        current = cls.get(action_id)
        if shortcut in current:
            current.remove(shortcut)
            return cls.set(action_id, current)
        return False

    @classmethod
    def clear_action(cls, action_id: str) -> bool:
        """Clear all shortcuts for an action (effectively disabling it)."""
        return cls.set(action_id, [])

    @classmethod
    def reset_action(cls, action_id: str) -> bool:
        """Reset a single action back to its built-in default shortcuts."""
        defaults = cls.get_default(action_id)
        return cls.set(action_id, list(defaults))

    @classmethod
    def reset_all(cls) -> bool:
        """Reset all actions to their built-in defaults and save."""
        cls._reset_to_defaults()
        logger.info("All shortcuts reset to defaults.")
        return cls.save()

    @classmethod
    def is_disabled(cls, action_id: str) -> bool:
        """Check if an action has no shortcuts assigned."""
        return len(cls.get(action_id)) == 0

    @classmethod
    def is_modified(cls, action_id: str) -> bool:
        """Check if an action's shortcuts differ from built-in defaults."""
        return cls.get(action_id) != cls.get_default(action_id)

    @classmethod
    def find_conflict(cls, shortcut: str, exclude_action_id: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        Check if a shortcut is already assigned to any other action.
        Comparison is normalized (case-insensitive key sequences).
        Returns tuple of (conflicting_action_id, conflicting_label), or None if no conflict.
        """
        shortcut_norm = shortcut.strip().lower()
        if not shortcut_norm:
            return None

        if not cls._current_shortcuts:
            cls.load()

        for act_id, sc_list in cls._current_shortcuts.items():
            if exclude_action_id and act_id == exclude_action_id:
                continue
            for sc in sc_list:
                if sc.strip().lower() == shortcut_norm:
                    label = DEFAULT_SHORTCUTS.get(act_id, {}).get("label", act_id)
                    return (act_id, label)
        return None

    @classmethod
    def get_all_with_info(cls) -> Dict[str, dict]:
        """Return dict with full info for all actions."""
        if not cls._current_shortcuts:
            cls.load()
        result = {}
        for action_id, info in DEFAULT_SHORTCUTS.items():
            current = cls._current_shortcuts.get(action_id, list(info["shortcuts"]))
            result[action_id] = {
                "label": info["label"],
                "category": info["category"],
                "shortcuts": list(current),
                "default_shortcuts": list(info["shortcuts"]),
                "is_disabled": len(current) == 0,
                "is_modified": current != info["shortcuts"],
            }
        return result

    @classmethod
    def get_categories(cls) -> List[str]:
        """Return unique categories sorted according to preferred CATEGORY_ORDER."""
        cats = {info["category"] for info in DEFAULT_SHORTCUTS.values()}
        return [c for c in CATEGORY_ORDER if c in cats] + sorted(cats - set(CATEGORY_ORDER))
