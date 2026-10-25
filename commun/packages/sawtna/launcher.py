"""Launch the three API processes plus Vite with one foreground command."""
import argparse
import os
import socket
import subprocess
import sys
import time
import httpx
from .config import ROOT, data_root


def wait_healthy(url, process, timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Le processus a quitté avec le code {process.returncode}. Consultez commun/data/runtime/logs.")
        try:
            if httpx.get(url, timeout=2).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(.3)
    raise RuntimeError(f"Service non disponible : {url}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-web", action="store_true")
    args = parser.parse_args()
    env = os.environ.copy()
    ports = {name: int(env.get(f"SAWTNA_{name.upper()}_PORT", value)) for name, value in {"api": 8010, "nlp": 8011, "analytics": 8012, "web": 5175}.items()}
    for name, port in ports.items():
        if args.no_web and name == "web":
            continue
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                raise SystemExit(f"Port {port} occupé ({name}). Changez SAWTNA_{name.upper()}_PORT.")
    env.update(SAWTNA_NLP_URL=f"http://127.0.0.1:{ports['nlp']}",
        SAWTNA_ANALYTICS_URL=f"http://127.0.0.1:{ports['analytics']}",
        SAWTNA_API_URL=f"http://127.0.0.1:{ports['api']}",
        SAWTNA_BACKEND_URL=f"http://127.0.0.1:{ports['api']}",
        SAWTNA_WEB_DIST=str(ROOT / "partie-4-frontend/dist"))
    processes, handles = [], []
    log_dir = data_root() / "runtime/logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    try:
        for module, port in [("nlp", ports["nlp"]), ("analytics", ports["analytics"]), ("backend", ports["api"])]:
            handle = (log_dir / f"{module}.log").open("a", encoding="utf-8")
            handles.append(handle)
            command = [sys.executable, "-m", "uvicorn", f"sawtna.{module}:app", "--host", "127.0.0.1", "--port", str(port), "--no-access-log"]
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=handle, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            processes.append(process)
            wait_healthy(f"http://127.0.0.1:{port}/health", process)
        if not args.no_web:
            web = ROOT / "partie-4-frontend"
            command = ["node", str(web / "node_modules/vite/bin/vite.js"), "--host", "127.0.0.1", "--port", str(ports["web"]), "--strictPort"]
            handle = (log_dir / "web.log").open("a", encoding="utf-8")
            handles.append(handle)
            process = subprocess.Popen(command, cwd=web, env=env, stdout=handle, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            processes.append(process)
            wait_healthy(f"http://127.0.0.1:{ports['web']}", process)
        print(f"Interface citoyen : http://127.0.0.1:{ports['web']}", flush=True)
        print(f"Dashboard : http://127.0.0.1:{ports['analytics']}/dashboard", flush=True)
        print(f"API : http://127.0.0.1:{ports['api']}/docs", flush=True)
        print("Ctrl+C pour arrêter les services. Journaux : commun/data/runtime/logs", flush=True)
        while all(p.poll() is None for p in processes):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
        for handle in handles:
            handle.close()


if __name__ == "__main__":
    main()
