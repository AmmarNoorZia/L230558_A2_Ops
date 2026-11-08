# VisionGuard: Step 1 (Windows)

Project name requirement: **YOUR_ROLL_NUMBER_A2_Ops** everywhere (GitHub, DagsHub, cloud). Rename this extracted folder after entering your own roll number, and edit `.env.example` into a local `.env` without committing it.

## Immediate steps
1. Extract this ZIP to `Desktop\\YOUR_ROLL_NUMBER_A2_Ops` (not to OneDrive if possible).
2. Double-click `01_SETUP.bat`. Requires installed **Python 3.11 (64-bit)**. Save a screenshot of the last environment report, including GPU detection. **On native Windows, TensorFlow >= 2.11 generally reports no GPU even with an NVIDIA GPU.** GPU training can be moved to Colab in Task 2.
3. Download the assigned dataset from https://www.kaggle.com/datasets/cashbowman/ai-generated-images-vs-real-images and unzip its contents under `data/raw/`. Confirm folder names such as `AiArtData` and `RealArt` remain intact. Kaggle requires an account for some downloads. **The file is large; downloading it can be the critical-path delay.** Optional CLI after login: `.venv\\Scripts\\kaggle.exe datasets download -d cashbowman/ai-generated-images-vs-real-images -p data/raw --unzip`.
4. Double-click `02_ANALYZE_DATA.bat` (audits all images, produces figures, and makes de-duplicated, stratified train/val/test CSV lists capped at 600 per class for faster training).
5. After installing Git for Windows, double-click `03_DVC_TOY.bat`; this demonstrates 2 commits and data restoration via a local remote. The toy commit identity is clearly labeled as a demonstration. Then double-click `04_DVC_DATA.bat` to track dataset bytes with DVC using a local remote. **CAUTION:** Keeping data in the original folder, DVC cache, and local remote can take ~3x the extracted dataset size. If short on disk or time, defer 04.

## Evidence produced
`outputs/environment.json`, `outputs/pip_freeze.txt`, `outputs/full_image_audit.csv`, `outputs/class_summary.csv`, `outputs/dataset_stats.json`, `outputs/sample_grid.png`, `outputs/feature_histograms.png`, `outputs/train_split.csv`, `outputs/val_split.csv`, `outputs/test_split.csv`, and `outputs/task1_report_notes.md`.

## Honest documentation
- The FULL dataset is audited; a reproducible subset is used for fast training due to time constraints. State both numbers in your report.
- DVC toy versions and the local remote are genuine local actions. For the grading rubric, the project must also be added to the required **DagsHub** repository with evidence of commits; connecting the remote GitHub/DagsHub account is a separate step.
- No credentials or screenshots are bundled or fabricated. Capture screenshots from your own actual runs.
- Scripts are AI-assisted and should be disclosed in your submitted report as required by assignment instructions.
- If the assigned data has a different folder structure, send a screenshot of the top-level folder names so the class loader can be adjusted quickly.
