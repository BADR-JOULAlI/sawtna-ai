"""Mechanical UTF-8/newline normalization of authored sources."""
import argparse
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("root",type=Path)
args=parser.parse_args()
for path in args.root.rglob("*"):
    if not path.is_file() or any(part in {".git","node_modules","dist","raw","processed","manifests","models",".venv","__pycache__"} for part in path.relative_to(args.root).parts):
        continue
    if path.suffix.lower() not in {".py",".md",".toml",".yml",".yaml",".json",".txt"} and path.name not in {".gitignore",".gitattributes","Dockerfile"}:
        continue
    try:
        text=path.read_text(encoding="utf-8")
    except UnicodeError:
        continue
    normalized=text.rstrip()+"\n"
    if normalized!=text:
        path.write_text(normalized,encoding="utf-8",newline="\n")
