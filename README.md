# Data Science in Cyber — Final Project

Critical reproduction and evaluation of **PhreshPhish** (Dalton et al., 2025) for phishing website detection.

## Project description

This project evaluates whether claims in the PhreshPhish paper are supported by data and experiments. The authors argue that many phishing ML studies report inflated performance due to low-quality data, train–test leakage, and unrealistic class balance. They release a large dataset and benchmark suite with realistic phishing base rates.

We reproduce a simplified pipeline: URL/HTML feature extraction, exploratory data analysis, and comparison of classical ML models (Logistic Regression, Random Forest).

## Links

| Resource | URL |
|----------|-----|
| **Selected paper** | https://arxiv.org/pdf/2507.10854 |
| **Original GitHub** | https://github.com/PhreshPhish/phreshphish |
| **Dataset** | https://huggingface.co/datasets/phreshphish/phreshphish |

## Repository structure

```
??? README.md
??? requirements.txt
??? notebooks/
?   ??? phreshphish_analysis.ipynb   # Main analysis notebook
??? src/
?   ??? features.py                  # URL/HTML feature extraction
??? report/
    ??? (final PDF report — add before submission)
```

## Execution instructions

### 1. Clone and install

```bash
git clone https://github.com/ayakhawalid/Data-Science-in-Cyber-Final-Project.git
cd Data-Science-in-Cyber-Final-Project
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the notebook

```bash
jupyter notebook notebooks/phreshphish_analysis.ipynb
```

Run all cells top to bottom. The first run downloads a **subset** of PhreshPhish from Hugging Face (not the full 36 GB dataset).

### 3. Configuration

In the notebook, adjust:

- `TRAIN_SAMPLE_SIZE` — default `20000`
- `TEST_SAMPLE_SIZE` — default `5000`
- `LOW_BASE_RATE` — default `0.01` (1% phishing) for realistic evaluation

## Dataset source

**PhreshPhish** — phishing and benign webpage URL + HTML pairs.

- Hugging Face: `phreshphish/phreshphish`
- Splits: `train`, `test`
- License: CC BY 4.0 (anti-phishing research only)

## Submission checklist

- [ ] PDF report (English)
- [ ] Executable notebook
- [ ] README with links and instructions
- [ ] Public GitHub repository

**Deadline:** Friday, July 10, 2026, 23:59
