import hashlib
import json
import sys
from types import SimpleNamespace

import pytest

from data_engineering.pipeline import extract_pdf
from data_engineering.review import audit_corpus


def test_arabic_ocr_keeps_logical_order_and_records_confidence(tmp_path, monkeypatch):
    """Exercise the OCR boundary without downloading models during unit tests."""
    model = tmp_path / "ara.traineddata"
    model.write_bytes(b"test-model")
    monkeypatch.setenv("SAWTNA_OCR_AR_TESSDATA", str(tmp_path))
    expected = ["النص الأول 2026 محفوظ بالترتيب المنطقي دون عكس الأرقام أو الكلمات.",
                "النص الثاني يحتاج إلى مراجعة الأرقام والكلمات في المصدر الرسمي."]
    class API:
        def __init__(self, **kwargs):
            assert kwargs["lang"] == "ara"
            self.index = -1
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def SetImageBytes(self, *args): self.index += 1
        def SetSourceResolution(self, dpi): assert dpi == 300
        def GetUTF8Text(self): return expected[self.index]
        def MeanTextConf(self): return [93, 65][self.index]
    class Page:
        def get_pixmap(self, **kwargs):
            assert kwargs["dpi"] == 300 and kwargs["alpha"] is False
            return SimpleNamespace(samples=b"pixels", width=1, height=1, n=3, stride=3)
    class Document(list):
        def __enter__(self): return self
        def __exit__(self, *_): pass
    monkeypatch.setitem(sys.modules, "tesserocr", SimpleNamespace(PyTessBaseAPI=API, PSM=SimpleNamespace(AUTO=3), __version__="test"))
    import pymupdf
    monkeypatch.setattr(pymupdf, "open", lambda _: Document([Page(), Page()]))
    details = []
    result = extract_pdf(tmp_path / "fixture.pdf", ocr=True, language="ar", details=details)
    assert result == [(1, expected[0]), (2, expected[1])]
    assert details[0]["flags"] == ["ocr_review_required"]
    assert details[1]["flags"] == ["ocr_review_required", "low_ocr_confidence"]
    assert details[0]["model_sha256"] == hashlib.sha256(model.read_bytes()).hexdigest()


def test_arabic_ocr_missing_model_fails_clearly(tmp_path, monkeypatch):
    monkeypatch.setenv("SAWTNA_OCR_AR_TESSDATA", str(tmp_path))
    monkeypatch.setitem(sys.modules, "tesserocr", SimpleNamespace())
    with pytest.raises(ValueError, match="--variant best"):
        extract_pdf(tmp_path / "fixture.pdf", ocr=True, language="ar")


def test_audit_does_not_hide_ocr_warning_on_otherwise_readable_text(tmp_path):
    raw = tmp_path / "raw/doc/original.pdf"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"%PDF-test-original")
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    source = tmp_path / "passages.jsonl"
    source.write_text(json.dumps({"id": "p1", "document_id": "doc", "title": "Source test",
                                 "text": "Un texte lisible peut encore contenir une erreur de chiffres produite par OCR.",
                                 "source_url": "https://maroc.ma/doc.pdf", "page": 1, "sha256": digest}) + "\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{"id": "doc", "format": "pdf", "pages": 1, "passages": 1,
                                     "path": "raw/doc/original.pdf", "sha256": digest,
                                     "final_url": "https://maroc.ma/doc.pdf", "download_status": "downloaded",
                                     "page_quality": [{"page": 1, "method": "ocr", "flags": ["low_ocr_confidence"]}]}]), encoding="utf-8")
    report = audit_corpus(source, manifest, tmp_path, tmp_path / "review")
    assert report["summary"]["errors"] == 0
    assert set(report["warnings"]["p1"]) == {"low_ocr_confidence", "ocr_review_required"}
    assert json.loads((tmp_path / "review/decisions.jsonl").read_text())["decision"] == "pending"
