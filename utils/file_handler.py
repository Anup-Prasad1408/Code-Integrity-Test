from __future__ import annotations

import codecs
import hashlib
import re
from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from utils.language_detector import detect_language, get_extension, is_supported_extension

MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_FILES_PER_BATCH = 20
ALLOWED_UPLOAD_EXTENSIONS = {".py", ".js", ".c", ".txt", ".pdf"}

def _safe_filename(filename: str) -> str:
    normalized = str(filename or "").replace("\\", "/")
    return Path(normalized).name.strip()

def validate_filename(filename: str) -> tuple[bool, str]:
    safe_name = _safe_filename(filename)
    if not safe_name:
        return False, "Filename is missing."
    if safe_name in {".", ".."} or safe_name.startswith("."):
        return False, "Hidden or invalid filenames are not allowed."
    if "\x00" in safe_name:
        return False, "Filename contains an invalid character."
    return True, ""

def validate_extension(filename: str) -> tuple[bool, str]:
    ext = get_extension(filename)
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        return False, f"Unsupported file type '{ext or '(none)'}'. Allowed: .py, .js, .c, .txt, .pdf."
    return True, ""

def validate_file_size(file_size: int) -> tuple[bool, str]:
    if file_size <= 0:
        return False, "File is empty."
    if file_size > MAX_FILE_SIZE:
        return False, f"File exceeds the {MAX_FILE_SIZE // (1024 * 1024)} MB per-file limit."
    return True, ""

def decode_source(raw_bytes: bytes) -> tuple[bool, str, str]:
    if not raw_bytes:
        return False, "", "File is empty."
    try:
        if raw_bytes.startswith(codecs.BOM_UTF8):
            text = raw_bytes.decode("utf-8-sig")
            encoding = "UTF-8 with BOM"
        elif raw_bytes.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            text = raw_bytes.decode("utf-16")
            encoding = "UTF-16"
        else:
            text = raw_bytes.decode("utf-8")
            encoding = "UTF-8"
    except UnicodeDecodeError:
        return False, "", "Unable to decode file. Use UTF-8 or BOM-marked UTF-16 text."
    if "\x00" in text:
        return False, "", "Binary content detected; source files must be text."
    if not text.strip():
        return False, "", "File contains no source code."
    return True, text, encoding

def extract_pdf_text(raw_bytes: bytes) -> tuple[bool, str, str]:
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(raw_bytes))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                return False, "", "PDF is encrypted and could not be opened."
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages).strip()
        if not text:
            return False, "", "No selectable text was found. Scanned/image-only PDFs need OCR, which is not included yet."
        return True, text, f"PDF text · {len(reader.pages)} page(s)"
    except ImportError:
        return False, "", "PDF support requires pypdf. Install dependencies with: python -m pip install -r requirements.txt"
    except Exception as exc:
        return False, "", f"Could not read PDF: {type(exc).__name__}: {exc}"

def _make_record(filename: str, raw_bytes: bytes, content: str, encoding: str, language: str) -> dict:
    digest = hashlib.sha256(raw_bytes).hexdigest()
    identity = hashlib.sha256(f"{filename}\0{digest}".encode("utf-8")).hexdigest()[:16]
    return {
        "valid": True, "id": identity, "name": filename, "extension": get_extension(filename),
        "language": language, "size": len(raw_bytes), "encoding": encoding,
        "line_count": len(content.splitlines()), "sha256": digest, "content": content,
    }

def validate_and_process_file(uploaded_file: Any, generic_language: str = "Python") -> dict:
    filename = _safe_filename(getattr(uploaded_file, "name", ""))
    ok, msg = validate_filename(filename)
    if not ok:
        return {"valid": False, "name": filename or "Unknown file", "error": msg}
    ok, msg = validate_extension(filename)
    if not ok:
        return {"valid": False, "name": filename, "error": msg}
    try:
        raw = uploaded_file.getvalue()
    except Exception:
        return {"valid": False, "name": filename, "error": "Could not read uploaded file."}
    if not isinstance(raw, (bytes, bytearray)):
        return {"valid": False, "name": filename, "error": "Uploaded content is not a byte stream."}
    raw = bytes(raw)
    ok, msg = validate_file_size(len(raw))
    if not ok:
        return {"valid": False, "name": filename, "size": len(raw), "error": msg}
    ext = get_extension(filename)
    if ext == ".pdf":
        ok, content, detail = extract_pdf_text(raw)
        language = generic_language
        encoding = detail
    else:
        ok, content, detail = decode_source(raw)
        language = detect_language(filename) or generic_language
        encoding = detail
    if not ok:
        return {"valid": False, "name": filename, "size": len(raw), "error": detail}
    if language not in {"Python", "JavaScript", "C"}:
        return {"valid": False, "name": filename, "error": "Choose Python, JavaScript or C for this text document."}
    return _make_record(filename, raw, content, encoding, language)

def process_multiple_files(uploaded_files: list[Any], generic_language: str = "Python") -> tuple[list[dict], list[dict]]:
    valid_files, invalid_files = [], []
    for index, uploaded in enumerate(uploaded_files):
        name = _safe_filename(getattr(uploaded, "name", "")) or "Unknown file"
        if index >= MAX_FILES_PER_BATCH:
            invalid_files.append({"valid": False, "name": name, "error": f"Batch limit is {MAX_FILES_PER_BATCH} files."})
            continue
        result = validate_and_process_file(uploaded, generic_language)
        (valid_files if result.get("valid") else invalid_files).append(result)
    return valid_files, invalid_files

def create_source_archive(files: list[dict]) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        for index, item in enumerate(files, 1):
            name = _safe_filename(item.get("name", "")) or f"source_{index}.txt"
            archive.writestr(f"{index:02d}_{name}", item.get("content", "").encode("utf-8"))
    return buffer.getvalue()
