"""Arabic OCR in logical reading order, without reconstructing a PDF text layer."""
import hashlib
import os
from pathlib import Path

from sawtna.config import data_root
from .quality import quality_flags


def extract_arabic_pdf(path: Path, details=None):
    import pymupdf as fitz
    try:
        import tesserocr
    except ImportError as exc:
        raise ValueError('OCR arabe : installer python -m pip install -e ".[ocr]".') from exc
    tessdata = Path(os.getenv("SAWTNA_OCR_AR_TESSDATA", str(data_root() / "models/tessdata-best"))).resolve()
    model = tessdata / "ara.traineddata"
    if not model.is_file():
        raise ValueError("Modèle OCR arabe absent : python commun/scripts/download_ocr.py --language ara --variant best")
    model_hash = hashlib.sha256(model.read_bytes()).hexdigest()
    pages = []
    # Tesseract returns logical Unicode order directly, avoiding RTL inversions
    # and column interleaving introduced by a second PDF text extraction step.
    with fitz.open(path) as doc, tesserocr.PyTessBaseAPI(
            path=str(tessdata), lang="ara", psm=tesserocr.PSM.AUTO) as api:
        for index, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300, colorspace=fitz.csRGB, alpha=False)
            api.SetImageBytes(pix.samples, pix.width, pix.height, pix.n, pix.stride)
            api.SetSourceResolution(300)
            text = api.GetUTF8Text().strip()
            confidence = api.MeanTextConf()
            flags = quality_flags(text) + ["ocr_review_required"]
            if confidence < 80:
                flags.append("low_ocr_confidence")
            pages.append((index + 1, text))
            if details is not None:
                details.append({"page": index + 1, "method": "ocr", "flags": flags,
                                "engine": f"tesserocr-{tesserocr.__version__}",
                                "dpi": 300, "model_sha256": model_hash,
                                "mean_confidence": confidence})
    return pages
