"""Assignment 1.2-1.3 plus reproducible stratified split lists for Task 2.

Usage: python scripts/audit_and_eda.py --data-dir data/raw --per-class 600
All images in dataset are AUDITED; only up to --per-class per label are used for quick training.
SHA256 groups are de-duplicated before the split to prevent cross-split leakage.
"""
import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, UnidentifiedImageError
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif"}


def classify(path: Path, base: Path):
    """Identify the label from an enclosing class directory (never from filename)."""
    folders = [p.lower().replace("_", "").replace("-", "").replace(" ", "") for p in path.relative_to(base).parts[:-1]]
    for f in reversed(folders):
        if f in {"aiartdata", "aigenerated", "aigeneratedimages", "aigeneratedart", "aiart", "synthetic", "fake", "ai"}:
            return "AI-generated"
        if f in {"realart", "realimages", "realimage", "realphotos", "real", "human", "authentic"}:
            return "Real"
    return None


def sha256_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit(base: Path):
    image_paths = sorted(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in EXTS)
    if not image_paths:
        raise RuntimeError(f"No image files found in {base}. Unzip the Kaggle dataset into data/raw first.")
    print(f"Scanning {len(image_paths):,} image files, including SHA-256 hashes...")
    rows = []
    for i, path in enumerate(image_paths, 1):
        label = classify(path, base)
        row = dict(path=path.relative_to(ROOT).as_posix(), class_label=label or "Unknown", file_size_bytes=path.stat().st_size,
                   width=None, height=None, color_mode=None, image_format=None, sha256=None, corrupt=False)
        try:
            row["sha256"] = sha256_file(path)
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                row.update(width=im.width, height=im.height, color_mode=im.mode, image_format=im.format)
        except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
            row["corrupt"] = True
            row["error"] = str(exc)[:120]
        rows.append(row)
        if i % 1000 == 0:
            print(f"  scanned {i:,}/{len(image_paths):,}", flush=True)
    return pd.DataFrame(rows)


def plots(df):
    labels = ["AI-generated", "Real"]
    fig, axs = plt.subplots(2, 5, figsize=(15, 7))
    random.seed(42)
    for j, lab in enumerate(labels):
        sampled = df[df.class_label == lab].sample(n=min(5, sum(df.class_label == lab)), random_state=42)
        for i, (_, r) in enumerate(sampled.iterrows()):
            ax = axs[j, i]
            try:
                with Image.open(ROOT / r.path) as im:
                    im.thumbnail((300, 240))
                    ax.imshow(im.convert("RGB"))
            except OSError:
                ax.text(0.5, 0.5, "Unreadable", ha="center")
            ax.axis("off")
            if i == 0:
                ax.set_title(lab, fontsize=12)
    fig.suptitle("Task 1.3: Sample images by class", fontsize=16)
    fig.tight_layout()
    fig.savefig(OUT / "sample_grid.png", dpi=150)
    plt.close(fig)

    cols = [("width", "Image width (px)"), ("height", "Image height (px)"), ("file_size_bytes", "File size (bytes)")]
    fig, axs = plt.subplots(2, 3, figsize=(15, 7))
    for i, lab in enumerate(labels):
        part = df[df.class_label == lab]
        for j, (col, xlabel) in enumerate(cols):
            vals = pd.to_numeric(part[col], errors="coerce").dropna()
            axs[i, j].hist(vals, bins=30, color="#3478cf", alpha=.85)
            axs[i, j].set_title(f"{lab}: {xlabel}")
            axs[i, j].set_xlabel(xlabel)
            axs[i, j].set_ylabel("Count")
    fig.suptitle("Task 1.3: Image characteristics per class", fontsize=16)
    fig.tight_layout()
    fig.savefig(OUT / "feature_histograms.png", dpi=150)
    plt.close(fig)


def summary_text(all_df, clean):
    summ = clean.groupby("class_label").agg(
        image_count=("path", "count"),
        width_min=("width", "min"), width_median=("width", "median"), width_max=("width", "max"),
        height_min=("height", "min"), height_median=("height", "median"), height_max=("height", "max"),
        size_min=("file_size_bytes", "min"), size_median=("file_size_bytes", "median"), size_max=("file_size_bytes", "max"),
    ).reset_index()
    summ.to_csv(OUT / "class_summary.csv", index=False)
    duplicated = all_df[all_df.duplicated("sha256", keep=False) & all_df.sha256.notna()]
    duplicate_extra = int(all_df.loc[all_df.sha256.notna(), "sha256"].duplicated().sum())
    stats = dict(
        total_image_files=len(all_df), valid_labeled_files=len(clean), corrupt_files=int(all_df.corrupt.sum()),
        unknown_label_files=int((all_df.class_label == "Unknown").sum()),
        duplicate_extra_files=duplicate_extra, duplicate_groups=int(duplicated.sha256.nunique()),
        class_counts=clean.class_label.value_counts().to_dict(),
    )
    (OUT / "dataset_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return stats, summ


def split_lists(clean, max_per_class):
    # Drop ambiguous cases where an identical content hash is assigned two class labels.
    ambiguous = clean.groupby("sha256").class_label.nunique()
    ambiguous_hashes = set(ambiguous[ambiguous > 1].index)
    clean = clean[~clean.sha256.isin(ambiguous_hashes)].drop_duplicates("sha256", keep="first")
    if max_per_class:
        parts = []
        for label in ["AI-generated", "Real"]:
            part = clean[clean.class_label == label]
            parts.append(part.sample(n=min(len(part), max_per_class), random_state=42))
        clean = pd.concat(parts, ignore_index=True)
    counts = Counter(clean.class_label)
    if min(counts.get("AI-generated", 0), counts.get("Real", 0)) < 10:
        raise RuntimeError(f"Too few examples of each class for a split: {counts}. Check dataset folders.")
    train, remaining = train_test_split(clean, test_size=.30, random_state=42, stratify=clean.class_label)
    val, test = train_test_split(remaining, test_size=.50, random_state=42, stratify=remaining.class_label)
    for name, part in [("train", train), ("val", val), ("test", test)]:
        part[["path", "class_label", "sha256"]].to_csv(OUT / f"{name}_split.csv", index=False)
    return {k: len(v) for k, v in [("train", train), ("val", val), ("test", test)]}, len(ambiguous_hashes)


def notes(stats, summary, lengths, ambiguous_count, per_class):
    summary_text = summary.to_string(index=False)
    lines = [
        "# VisionGuard — Task 1 evidence notes (edit into your own words)",
        "", "## 1.1 Environment", "See `environment.json` and `pip_freeze.txt`; screenshot terminal after `01_SETUP.bat`.",
        "", "## 1.2 Dataset audit", "The audit inspects every supported image file under `data/raw`, verifies decodability,",
        "records the dimensions, image format, colour mode, size and SHA-256 digest,",
        "and identifies exact duplicates using equal digests.",
        "", "```", summary_text, "```",
        "", f"Corrupt files: {stats['corrupt_files']}; extra exact duplicates: {stats['duplicate_extra_files']}; unknown-label files: {stats['unknown_label_files']}.",
        "", "## 1.3 EDA", "See `sample_grid.png` and `feature_histograms.png`.",
    ]
    for _, r in summary.iterrows():
        lines.append(f"- {r.class_label}: median width {r.width_median:g}px, height {r.height_median:g}px, file size {r.size_median:g} bytes; inspect histogram shape for outliers.")
    lines.extend(["", "## Reproducible model input", f"Training subset cap: {per_class} per class (after deduplication).", f"Ambiguous duplicate hash groups excluded: {ambiguous_count}.",
                  f"Deterministic stratified split: train={lengths['train']}, validation={lengths['val']}, test={lengths['test']}; random seed 42.",
                  "Data augmentation must be applied only to training. Do not use test images when tuning.",
                  "", "## 1.4 DVC", "Run `03_DVC_TOY.bat` and `04_DVC_DATA.bat` and take real screenshots;",
                  "the small .dvc pointer tracks content hashes and paths, while large bytes are stored in the DVC cache/remote.",
                  "", "## Screenshot checklist", "- [ ] Environment versions / GPU visibility", "- [ ] Class audit table and corrupt/duplicate counts", "- [ ] Sample grid", "- [ ] Per-class histograms", "- [ ] DVC initial and changed CSV Git commits", "- [ ] DVC push, remove, pull, and earlier-version checkout", "- [ ] DVC tracked dataset and configured remote", ""])
    (OUT / "task1_report_notes.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", default="data/raw")
    p.add_argument("--per-class", type=int, default=600,
                   help="Limit samples per class for quick model training (0=all). Full audit still scans everything.")
    args = p.parse_args()
    folder = ROOT / args.data_dir
    all_df = audit(folder)
    all_df.to_csv(OUT / "full_image_audit.csv", index=False)
    clean = all_df[(~all_df.corrupt) & all_df.class_label.isin(["AI-generated", "Real"])].copy()
    if clean.empty:
        raise RuntimeError("All labels were Unknown. Expected Kaggle folders such as AiArtData and RealArt.")
    stats, summ = summary_text(all_df, clean)
    plots(clean)
    lengths, ambiguous_count = split_lists(clean, args.per_class)
    notes(stats, summ, lengths, ambiguous_count, args.per_class)
    print("\n=== VISIONGUARD: TASK 1.2 / 1.3 ===")
    print("TOTAL:", stats["total_image_files"], "| CORRUPT:", stats["corrupt_files"],
          "| EXTRA EXACT DUPLICATES:", stats["duplicate_extra_files"])
    print("CLASS COUNTS:", stats["class_counts"])
    print("SPLITS:", lengths)
    print("Saved: outputs/full_image_audit.csv, class_summary.csv, sample_grid.png, feature_histograms.png")
    print("Saved: outputs/train_split.csv, val_split.csv, test_split.csv, task1_report_notes.md")

if __name__ == "__main__":
    main()
