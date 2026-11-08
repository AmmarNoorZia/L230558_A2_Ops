"""Task 1.4 apply: DVC-track dataset and push to a local remote.
This can temporarily require substantial disk space for DVC cache and remote.
"""
from pathlib import Path
import shutil
import subprocess
ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT.parent / "visionguard_dataset_remote"


def run(*args):
    print("$", " ".join(map(str, args)), flush=True)
    result = subprocess.run(list(map(str,args)), cwd=ROOT, text=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(map(str,args))}")


def main():
    if not shutil.which("git"):
        raise RuntimeError("Git for Windows is missing: install from git-scm.com first.")
    if not (ROOT / "data" / "raw").exists() or not any((ROOT / "data" / "raw").rglob("*.jpg")):
        # Some datasets may use PNG instead of JPG.
        if not any(p.suffix.lower() in {".jpg",".jpeg",".png",".webp"} for p in (ROOT / "data" / "raw").rglob("*")):
            raise RuntimeError("Place the unzipped dataset in data/raw first.")
    if not (ROOT / ".git").exists():
        run("git", "init")
    if not (ROOT / ".dvc").exists():
        run("dvc", "init")
    run("dvc", "remote", "add", "-f", "-d", "localstore", REMOTE)
    print("WARNING: DVC copies/cache the dataset; keep sufficient free disk space.")
    run("dvc", "add", "data/raw")
    run("dvc", "push")
    print("SUCCESS: dataset DVC pointer is data/raw.dvc; remote is", REMOTE)
    print("Run 'git add .dvc data/raw.dvc .gitignore data/.gitignore' then commit with YOUR identity.")
    print("Do not commit raw images, tokens, or .env.")

if __name__ == "__main__":
    main()
