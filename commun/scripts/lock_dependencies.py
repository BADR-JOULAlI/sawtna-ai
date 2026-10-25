"""Capture the versions from the locally verified backend Docker image."""
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[2]
result=subprocess.run(["docker","compose","exec","-T","backend","python","-m","pip","freeze"],cwd=root,check=True,capture_output=True,text=True)
lines=[line for line in result.stdout.splitlines() if line.strip() and not line.lower().startswith("sawtna")]
(root/"requirements.lock.txt").write_text("# Versions from the tested Linux image; regenerate after verification.\n"+"\n".join(lines)+"\n",encoding="utf-8")
print(f"{len(lines)} dépendances figées.")
