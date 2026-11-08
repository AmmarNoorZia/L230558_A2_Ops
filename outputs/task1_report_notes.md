# VisionGuard — Task 1 evidence notes (edit into your own words)

## 1.1 Environment
See `environment.json` and `pip_freeze.txt`; screenshot terminal after `01_SETUP.bat`.

## 1.2 Dataset audit
The audit inspects every supported image file under `data/raw`, verifies decodability,
records the dimensions, image format, colour mode, size and SHA-256 digest,
and identifies exact duplicates using equal digests.

```
 class_label  image_count  width_min  width_median  width_max  height_min  height_median  height_max  size_min  size_median  size_max
AI-generated          539        225        1024.0       6000         135          800.0        4001     11738     199760.0   5626183
        Real          435        183         940.0       8495         158          720.0        7091     11311     144982.0  10195352
```

Corrupt files: 0; extra exact duplicates: 1; unknown-label files: 0.

## 1.3 EDA
See `sample_grid.png` and `feature_histograms.png`.
- AI-generated: median width 1024px, height 800px, file size 199760 bytes; inspect histogram shape for outliers.
- Real: median width 940px, height 720px, file size 144982 bytes; inspect histogram shape for outliers.

## Reproducible model input
Training subset cap: 600 per class (after deduplication).
Ambiguous duplicate hash groups excluded: 0.
Deterministic stratified split: train=681, validation=146, test=146; random seed 42.
Data augmentation must be applied only to training. Do not use test images when tuning.

## 1.4 DVC
Run `03_DVC_TOY.bat` and `04_DVC_DATA.bat` and take real screenshots;
the small .dvc pointer tracks content hashes and paths, while large bytes are stored in the DVC cache/remote.

## Screenshot checklist
- [ ] Environment versions / GPU visibility
- [ ] Class audit table and corrupt/duplicate counts
- [ ] Sample grid
- [ ] Per-class histograms
- [ ] DVC initial and changed CSV Git commits
- [ ] DVC push, remove, pull, and earlier-version checkout
- [ ] DVC tracked dataset and configured remote
