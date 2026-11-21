from io import BytesIO
from utils.file_handler import process_multiple_files, validate_and_process_file, decode_source

class FakeUpload:
    def __init__(self, name, content):
        self.name = name
        self._content = content
    def getvalue(self):
        return self._content

def test_python_upload():
    result = validate_and_process_file(FakeUpload("main.py", b"print('hello')"))
    assert result["valid"] is True
    assert result["language"] == "Python"

def test_js_and_c_uploads():
    js = validate_and_process_file(FakeUpload("main.js", b"const x = 1;"))
    c = validate_and_process_file(FakeUpload("main.c", b"int main(){return 0;}"))
    assert js["language"] == "JavaScript"
    assert c["language"] == "C"

def test_txt_uses_selected_language():
    result = validate_and_process_file(FakeUpload("submission.txt", b"print('hello')"), "Python")
    assert result["valid"] and result["language"] == "Python"

def test_batch_isolates_invalid_files():
    valid, invalid = process_multiple_files([
        FakeUpload("ok.py", b"print(1)"),
        FakeUpload("bad.exe", b"no")
    ])
    assert len(valid) == 1 and len(invalid) == 1

def test_decode_binary_rejected():
    ok, _, _ = decode_source(b"\x00\x01\x02")
    assert not ok


def test_pdf_without_text_reports_extraction_error():
    # A syntactically invalid/empty PDF byte stream must be rejected with a useful reason.
    result = validate_and_process_file(FakeUpload("scan.pdf", b"not a pdf"), "Python")
    assert result["valid"] is False
    assert "Could not read PDF" in result["error"] or "PDF" in result["error"]
