import os
import sys
from dataclasses import dataclass

from dotenv import dotenv_values, load_dotenv, set_key

from paths import PROJECT_ROOT


ENV_PATH = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class SettingField:
    key: str
    label: str
    default: str = ""
    secret: bool = False


API_KEY_FIELDS = [
    SettingField("GEMINI_API_KEY", "Gemini API Key", secret=True),
    SettingField("GROQ_API_KEY", "Groq API Key", secret=True),
    SettingField("XAI_API_KEY", "xAI API Key", secret=True),
]

MODEL_FIELDS = [
    SettingField("SCRIPT_GENERATION_GEMINI_MODEL", "Script Gemini Model", "gemini-2.5-flash"),
    SettingField("SCRIPT_GENERATION_GROQ_MODEL", "Script Groq Model", "llama-3.3-70b-versatile"),
    SettingField("NEWS_VERIFICATION_GEMINI_MODEL", "News Verification Gemini Model", "gemini-1.5-flash"),
    SettingField("NEWS_VERIFICATION_GROQ_MODEL", "News Verification Groq Model", "llama-3.3-70b-versatile"),
    SettingField("TOPICWISE_NEWS_GEMINI_MODEL", "Topic-wise Gemini Model", "gemini-2.5-pro"),
    SettingField("TOPICWISE_NEWS_GROQ_MODEL", "Topic-wise Groq Model", "llama-3.3-70b-versatile"),
    SettingField("CHUNK_GENERATION_GROQ_MODEL", "Caption Chunk Groq Model", "llama-3.3-70b-versatile"),
    SettingField("NEWS_DEDUPLICATION_GROQ_MODEL", "News Deduplication Groq Model", "llama-3.3-70b-versatile"),
    SettingField("BACKIMAGE_IMAGE_MODEL", "Background Image Model", "grok-imagine-image"),
    SettingField("THUMBNAIL_IMAGE_MODEL", "Thumbnail Image Model", "grok-imagine-image"),
]

MODEL_MODULE_ATTRS = {
    "tasks.script_generator": {
        "SCRIPT_GENERATION_GEMINI_MODEL": "GEMINI_MODEL",
        "SCRIPT_GENERATION_GROQ_MODEL": "GROQ_MODEL",
    },
    "tasks.news_verifier": {
        "NEWS_VERIFICATION_GEMINI_MODEL": "GEMINI_MODEL",
        "NEWS_VERIFICATION_GROQ_MODEL": "GROQ_MODEL",
    },
    "tasks.ExtractionTools.topicwise_news_extractor": {
        "TOPICWISE_NEWS_GEMINI_MODEL": "TOPICWISE_NEWS_GEMINI_MODEL",
        "TOPICWISE_NEWS_GROQ_MODEL": "TOPICWISE_NEWS_GROQ_MODEL",
    },
    "tasks.chunk_generator": {
        "CHUNK_GENERATION_GROQ_MODEL": "CHUNK_GENERATION_GROQ_MODEL",
    },
    "tasks.ExtractionTools.deduplicator": {
        "NEWS_DEDUPLICATION_GROQ_MODEL": "GROQ_MODEL",
    },
    "tasks.backimage_generator": {
        "BACKIMAGE_IMAGE_MODEL": "DEFAULT_MODEL",
    },
    "tasks.thumbnail_generator": {
        "THUMBNAIL_IMAGE_MODEL": "DEFAULT_MODEL",
    },
}


def load_settings() -> dict[str, str]:
    load_dotenv(ENV_PATH, override=True)
    env_values = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}
    settings: dict[str, str] = {}

    for field in API_KEY_FIELDS + MODEL_FIELDS:
        settings[field.key] = os.getenv(field.key) or env_values.get(field.key) or field.default

    return settings


def save_settings(values: dict[str, str]) -> None:
    ENV_PATH.touch(exist_ok=True)

    for field in API_KEY_FIELDS + MODEL_FIELDS:
        value = (values.get(field.key) or "").strip()
        set_key(str(ENV_PATH), field.key, value)
        os.environ[field.key] = value

    refresh_runtime_settings()


def refresh_runtime_settings() -> None:
    for module_name, attr_map in MODEL_MODULE_ATTRS.items():
        module = sys.modules.get(module_name)
        if module is None:
            continue

        for env_key, attr_name in attr_map.items():
            setattr(module, attr_name, os.environ.get(env_key, ""))

    _refresh_clients()


def _refresh_clients() -> None:
    gemini_key = os.environ.get("GEMINI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")

    for module_name in (
        "tasks.script_generator",
        "tasks.news_verifier",
        "tasks.ExtractionTools.topicwise_news_extractor",
    ):
        module = sys.modules.get(module_name)
        if module is None:
            continue

        if hasattr(module, "genai"):
            module.gemini_client = module.genai.Client(api_key=gemini_key) if gemini_key else None
            if hasattr(module, "client"):
                module.client = module.genai.Client(api_key=gemini_key) if gemini_key else None
        if hasattr(module, "Groq"):
            module.groq_client = module.Groq(api_key=groq_key) if groq_key else None

        if hasattr(module, "gemini_api_key"):
            module.gemini_api_key = gemini_key
        if hasattr(module, "groq_api_key"):
            module.groq_api_key = groq_key

    chunk_module = sys.modules.get("tasks.chunk_generator")
    if chunk_module is not None and hasattr(chunk_module, "Groq"):
        chunk_module.api_key = groq_key
        chunk_module.client = chunk_module.Groq(api_key=groq_key) if groq_key else None

    dedup_module = sys.modules.get("tasks.ExtractionTools.deduplicator")
    if dedup_module is not None:
        dedup_module.GROQ_API_KEY = groq_key
