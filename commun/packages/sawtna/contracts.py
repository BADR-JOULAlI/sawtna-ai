from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

Language = Literal["fr", "ar", "darija"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Passage(StrictModel):
    id: str = Field(pattern=r"^[a-zA-Z0-9_.:-]{1,150}$")
    document_id: str = Field(pattern=r"^[a-zA-Z0-9_.:-]{1,100}$")
    title: str = Field(min_length=2, max_length=500)
    source_url: HttpUrl
    language: Language = "fr"
    text: str = Field(min_length=30, max_length=12000)
    section: str = Field(default="", max_length=300)
    page: int | None = Field(default=None, ge=1)
    status: Literal["reviewed", "pending_review", "synthetic"] = "pending_review"
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class EmbedRequest(StrictModel):
    texts: list[str] = Field(min_length=1, max_length=64)
    kind: Literal["query", "passage"] = "query"

    @field_validator("texts")
    @classmethod
    def limit_text(cls, values):
        if any(not value.strip() or len(value) > 12000 for value in values):
            raise ValueError("Chaque texte doit contenir entre 1 et 12000 caractères.")
        return values


class EmbedResponse(StrictModel):
    vectors: list[list[float]]
    model: str
    dimensions: int


class AskRequest(StrictModel):
    question: str = Field(min_length=3, max_length=1500)
    language: Language = "fr"

    @field_validator("question")
    @classmethod
    def strip_question(cls, value):
        if len(value.strip()) < 3:
            raise ValueError("La question est trop courte.")
        return value.strip()


class AnalyticsEvent(StrictModel):
    event_id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    event: Literal["question_answered", "question_unanswered", "quiz_completed"]
    language: Language
    latency_ms: int = Field(default=0, ge=0, le=600000)
    score: int = Field(default=0, ge=0, le=100)
