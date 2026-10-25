"""CPU NLP endpoint. Offline baseline and optional real multilingual E5 encoder."""
import hashlib
import os
import re
import unicodedata
from functools import lru_cache
import numpy as np
from fastapi import Depends, FastAPI
from sawtna.contracts import EmbedRequest, EmbedResponse
from sawtna.security import require_service

DIMENSIONS = 384
STOP = set("le la les de des du un une et en est sont que qui quel quelle quels quelles pour dans au aux a à ce cette se son sa ses sur il elle comment quoi the is are what how why chno ach wach bin l w kifach howa dyal كيف يتم ما هو هي من في عن اعضاء مجلس".split())
GROUPS = [
    ("election", "elections", "انتخابات", "الانتخابات", "intikhabat", "lintikhabat"),
    ("communales", "communale", "commune", "communes", "جماعية", "الجماعية", "الجماعات", "ljama3iya", "jama3iya", "jama3a", "جماعة"),
    ("legislatives", "legislative", "تشريعية", "التشريعية", "tachri3iya", "ltachri3iya"),
    ("representants", "representant", "النواب", "النوّاب", "nowab", "nouab"),
    ("parlement", "parlementaire", "برلمان", "البرلمان", "barlaman", "lbarlaman"),
    ("conseillers", "مستشارين", "المستشارين"),
    ("voter", "vote", "votent", "suffrage", "scrutin", "تصويت", "التصويت", "يصوت", "nsowet", "nswt", "tswit", "tasswit"),
    ("age", "ans", "سن", "السن", "عمر", "عام", "3am", "3mer", "ch7al"),
    ("inscription", "inscrire", "inscrit", "listes", "liste", "تسجيل", "التسجيل", "لوائح", "اللوائح", "tsjil", "nsjel"),
    ("egalite", "libre", "liberte", "حرية", "المساواة", "الحرية"),
    ("regions", "region", "جهة", "الجهات"),
    ("source", "sources", "مصدر", "مصادر"),
    ("elus", "elu", "elected", "انتخاب", "ينتخب", "ينتخبون", "kaytntakhbo", "ntakhbo"),
    ("droit", "droits", "حق", "حقوق", "الحق", "7e9", "l7e9", "7eqq"),
    ("personnel", "personnelle", "شخصي", "شخصية", "chakhsi"),
    ("conseil", "conseils", "مجالس", "المجالس", "majlis", "majalis"),
]
ALIASES = {token: f"concept{index}" for index, group in enumerate(GROUPS) for token in group}


def tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    words = re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)
    return [ALIASES.get(word, word) for word in words if word not in STOP]


def baseline(text: str) -> list[float]:
    vec = np.zeros(DIMENSIONS, dtype=np.float32)
    for word in tokens(text):
        digest = hashlib.sha256(word.encode()).digest()
        index = int.from_bytes(digest[:4], "little") % DIMENSIONS
        vec[index] += 2.0 if word.startswith("concept") else 1.0
    norm = float(np.linalg.norm(vec))
    return (vec / norm if norm else vec).tolist()


@lru_cache(maxsize=1)
def trained_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("intfloat/multilingual-e5-small", device=os.getenv("SAWTNA_MODEL_DEVICE", "cpu"))


def embed(texts: list[str], kind="query") -> EmbedResponse:
    provider = os.getenv("SAWTNA_EMBEDDER", "concept-hash-v1")
    if provider == "multilingual-e5-small":
        vectors = trained_model().encode([f"{kind}: {t}" for t in texts], normalize_embeddings=True).tolist()
        return EmbedResponse(vectors=vectors, model="intfloat/multilingual-e5-small", dimensions=DIMENSIONS)
    if provider != "concept-hash-v1":
        raise ValueError(f"Encodeur inconnu : {provider}")
    return EmbedResponse(vectors=[baseline(t) for t in texts], model=provider, dimensions=DIMENSIONS)


app = FastAPI(title="Sawtna NLP", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "nlp", "model": os.getenv("SAWTNA_EMBEDDER", "concept-hash-v1"), "dimensions": DIMENSIONS}


@app.post("/v1/embeddings", response_model=EmbedResponse, dependencies=[Depends(require_service)])
def embeddings(body: EmbedRequest):
    return embed(body.texts, body.kind)
