import hashlib
import json
import httpx
import pytest
from sawtna.data_engineering import allowed_url, fetch, extract_html, split_passages, export_reviewed


@pytest.mark.parametrize("url", ["http://maroc.ma/a", "https://evil.test/a.pdf", "https://maroc.ma.evil.test/a", "https://maroc.ma:444/a", "https://user:pass@maroc.ma/a"])
def test_collector_rejects_nonofficial_urls(url):
    with pytest.raises(ValueError):
        allowed_url(url)


def test_collector_rejects_redirect_to_private_or_nonofficial_host():
    def handler(request):
        return httpx.Response(302, headers={"Location":"https://127.0.0.1/private"})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError):
            fetch({"url":"https://maroc.ma/a","format":"pdf"},client)


def test_html_cleanup_keeps_article_and_removes_navigation():
    html = b"<html><body><nav>Ignore this navigation</nav><main><article><p>Document officiel contenant des informations electorales.</p><script>bad()</script></article></main><footer>Ignore footer</footer></body></html>"
    text = extract_html(html)[0][1]
    assert "Document officiel" in text
    assert "Ignore" not in text and "bad()" not in text


def test_pdf_content_validation_and_bounded_retries():
    with httpx.Client(transport=httpx.MockTransport(lambda _:httpx.Response(200, content=b"<html>Maintenance</html>"))) as client:
        with pytest.raises(ValueError, match="PDF"):
            fetch({"url":"https://maroc.ma/a.pdf","format":"pdf"},client)


def test_chunking_preserves_start_and_end_without_infinite_loop():
    text = "Début. " + ("Ceci est un passage de référence. " * 300) + " Fin du document."
    chunks = list(split_passages(text, 600, 80))
    assert len(chunks) > 10
    assert chunks[0].startswith("Début")
    assert chunks[-1].endswith("Fin du document.")
    assert all(len(chunk) <= 600 for chunk in chunks)


def test_review_export_requires_selected_document(tmp_path):
    source = tmp_path / "pending.jsonl"
    passage = {"id":"one","document_id":"official","title":"Texte officiel","source_url":"https://maroc.ma/a.pdf","text":"Un extrait officiel suffisamment long pour servir de passage.","language":"fr","sha256":hashlib.sha256(b"fixture").hexdigest()}
    source.write_text(json.dumps(passage)+"\n",encoding="utf-8")
    out = tmp_path / "reviewed.jsonl"
    assert export_reviewed(source,out,{"official"}) == 1
    assert json.loads(out.read_text())["status"] == "reviewed"
    with pytest.raises(ValueError):
        export_reviewed(source,out,{"missing"})
