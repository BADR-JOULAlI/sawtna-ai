"""Stable CLI path for the Data Engineering module."""
from data_engineering.pipeline import (
    ALLOWED_HOSTS, allowed_url, clean, collect, extract_html, extract_pdf,
    split_passages, export_reviewed, fetch, main,
)

if __name__ == "__main__":
    main()
