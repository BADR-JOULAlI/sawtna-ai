import os
import uvicorn

if __name__ == "__main__":
    service = os.getenv("SAWTNA_SERVICE", "backend")
    if service not in {"backend", "nlp", "analytics"}:
        raise SystemExit("SAWTNA_SERVICE doit être backend, nlp ou analytics")
    uvicorn.run(f"sawtna.{service}:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), access_log=False)
