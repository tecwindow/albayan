import UniversalSpeech as u_speech
from utils.settings import Config
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class UniversalSpeech:
    logger.debug("Initializing UniversalSpeech")
    try:
        universal_speech = u_speech.UniversalSpeech()
        universal_speech.enable_native_speech(False)
        reader = universal_speech.engine_used
        logger.debug(f"UniversalSpeech initialized. Using screen reader: {reader}")
    except Exception as e:
        universal_speech = None
        reader = None
        logger.warning(f"Failed to initialize UniversalSpeech: {e}")

    @classmethod
    def say(cls, msg: str, interrupt: bool = True, force: bool = False) -> None:
        if Config.audio.speak_actions_enabled or force:
            if cls.universal_speech is not None:
                try:
                    cls.universal_speech.say(msg, interrupt)
                    logger.debug(
                        f"Speaking: {msg} (Interrupt: {interrupt}, Force: {force})"
                    )
                except Exception as e:
                    logger.warning(f"UniversalSpeech.say failed: {e}")
            else:
                logger.debug(
                    f"Speech skipped (UniversalSpeech not available): '{msg}'"
                )
        else:
            logger.debug(f"Speech action skipped. Message: '{msg}' (Force: {force})")