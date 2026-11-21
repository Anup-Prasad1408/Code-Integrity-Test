from pathlib import Path

LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".c": "C",
}

def get_extension(filename: str) -> str:
    if not filename:
        return ""
    return Path(str(filename).replace("\\", "/")).suffix.lower()

def detect_language(filename: str) -> str | None:
    return LANGUAGE_MAP.get(get_extension(filename))

def is_supported_extension(filename: str) -> bool:
    return get_extension(filename) in LANGUAGE_MAP
