"""Self-contained local demonstration for Assignment 1.4 (no cloud credentials needed)."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "outputs" / "toy_dvc_lab"
REMOTE = ROOT / "outputs" / "toy_dvc_remote"


def run(*args, cwd=WORK):
    command = list(map(str, args))
    print("$", " ".join(command), flush=True)
    cp = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(cp.stdout[-3000:], flush=True)
    if cp.returncode:
        raise RuntimeError(f"Command failed ({cp.returncode}): {command}")
    return cp.stdout


def commit(message):
    # Toy-only commit identity, not a claim about a student author's identity.
    run("git", "-c", "user.name=VisionGuard Toy Lab", "-c", "user.email=toy-lab@example.invalid", "commit", "-m", message)


def main():
    if not shutil.which("git"):
        raise RuntimeError("Install Git for Windows (git-scm.com) and rerun.")
    if WORK.exists():
        shutil.rmtree(WORK)
    if REMOTE.exists():
        shutil.rmtree(REMOTE)
    WORK.mkdir(parents=True)
    REMOTE.mkdir(parents=True)
    run("git", "init")
    run("dvc", "init")
    run("dvc", "remote", "add", "-d", "localstore", REMOTE)
    (WORK / "scores.csv").write_text("epoch,accuracy\n1,0.70\n", encoding="utf-8")
    run("dvc", "add", "scores.csv")
    run("git", "add", ".")
    commit("Toy dataset version 1")
    v1 = run("git", "rev-parse", "HEAD").strip()
    run("dvc", "push")
    (WORK / "scores.csv").write_text("epoch,accuracy\n1,0.70\n2,0.82\n", encoding="utf-8")
    run("dvc", "add", "scores.csv")
    run("git", "add", "scores.csv.dvc")
    commit("Toy dataset version 2")
    run("dvc", "push")
    run("git", "log", "--oneline", "-2")
    # Demonstrate remote recovery for newest version.
    (WORK / "scores.csv").unlink()
    run("dvc", "pull")
    print("Recovered latest CSV:", (WORK / "scores.csv").read_text())
    # Check out only its pointer file from the first commit; do not rewind Git HEAD.
    run("git", "checkout", v1, "--", "scores.csv.dvc")
    run("dvc", "checkout")
    print("Recovered older CSV:", (WORK / "scores.csv").read_text())
    print("TOY COMPLETE: screenshot the above two recovered CSV outputs and commits.")
    print("Toy repo:", WORK)

if __name__ == "__main__":
    main()
