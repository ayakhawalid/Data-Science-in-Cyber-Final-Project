# Data Science in Cyber - Final Project

**Student:** Aya Khawaled (ID: 214742496)

Critical reproduction and evaluation of **PhreshPhish** (Dalton et al., 2025) for phishing website detection.

## Project description

This project evaluates whether claims in the PhreshPhish paper are supported by data and experiments. The authors argue that many phishing ML studies report inflated performance due to low-quality data, train-test leakage, and unrealistic class balance. They release a large dataset and benchmark suite with realistic phishing base rates.

We reproduce a simplified pipeline: URL/HTML feature extraction, exploratory data analysis, and comparison of classical ML models (Logistic Regression and Random Forest). We also compare high-prevalence test metrics with a simulated ~1% phishing deployment benchmark.

## Links

| Resource | URL |
|----------|-----|
| Selected paper | https://arxiv.org/pdf/2507.10854 |
| Original GitHub repository | https://github.com/PhreshPhish/phreshphish |

## Execution instructions

### 1. Clone and install

```bash
git clone https://github.com/ayakhawalid/Data-Science-in-Cyber-Final-Project.git
cd Data-Science-in-Cyber-Final-Project
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the notebook

```bash
jupyter notebook notebooks/phreshphish_analysis.ipynb
```

Run all cells from top to bottom. The first run streams a subset of PhreshPhish from Hugging Face and caches features under `data/`. Later runs load from cache unless `FORCE_REBUILD_CACHE = True` in the first notebook cell.

Main configuration (notebook cell 1): `TRAIN_SAMPLE_SIZE = 5_000`, `TEST_SAMPLE_SIZE = 1_000`, `MAX_HTML_CHARS = 80_000`.

### 3. Report

The PDF report is in `report/phreshphish_final_report.pdf`. Supporting code is in `src/features.py` and `src/data_cache.py`.

## Dataset source

**PhreshPhish** - phishing and benign webpage URL + HTML pairs.

- Hugging Face: https://huggingface.co/datasets/phreshphish/phreshphish
- Splits: `train`, `test`
- License: CC BY 4.0 (anti-phishing research only)

This project uses a streamed subset (5,000 train + 1,000 test rows), not the full ~36 GB dataset.
