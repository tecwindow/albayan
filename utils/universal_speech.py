import  UniversalSpeech as u_speech
from utils.settings import SettingsManager

class UniversalSpeech:
    universal_speech = u_speech.UniversalSpeech()
    universal_speech.enable_native_speech(False)

    @classmethod
    def say(cls, msg: str, interrupt: bool = True) -> None:
        if SettingsManager.current_settings["audio"]["speak_actions_enabled"]:
            cls.universal_speech.say(msg, interrupt)

