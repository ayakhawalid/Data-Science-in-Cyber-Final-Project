# PhreshPhish Project — Study Notes

**Student:** Aya Khawaled (ID: 214742496)  
**Purpose:** Quick reference for metrics, models, data loading, and the claim we tested.

---

## 1. The claim we tested

**PhreshPhish claim (base rate):** Many phishing papers report **inflated** precision/F1 because test sets have **too much phishing** (~33–50%), while real deployment is often **~0.05%–1%**.

**What we did:** Same models, same features, same threshold (0.5), two evaluations:

| Evaluation | Phishing % | What it simulates |
|------------|------------|-------------------|
| Official-style **test** | ~45% | Lab / paper-style test set |
| **1% benchmark** | ~1% | Deployment-like rarity |

**Conclusion:** We **support** this claim. Precision and F1 dropped sharply at 1%; ROC-AUC and recall stayed high.

**What we did NOT test:** Leakage, old-dataset quality, full official 975 benchmarks.

---

## 2. How we loaded data (RAM)

Full PhreshPhish is **~36 GB** — cannot load all into RAM.

### First run (slow, uses internet)

1. `load_dataset(..., streaming=True)` — **one row at a time** from Hugging Face.
2. Keep only **5,000 train + 1,000 test** rows.
3. Truncate HTML to **80,000 chars** per row (`MAX_HTML_CHARS`).
4. `gc.collect()` every 500 rows to free memory.
5. Extract **19 numeric features** from URL + HTML.
6. Save to disk:
   - `data/train_features.parquet`, `data/test_features.parquet`
   - `data/train_meta.parquet`, `data/test_meta.parquet` (no HTML)
   - `data/cache_manifest.json` (records sample sizes)

### Later runs (fast, low RAM)

- If cache matches config → **read parquet from disk**, skip download and HTML.
- Set `FORCE_REBUILD_CACHE = True` to re-stream from Hugging Face.

```
First run:  Hugging Face → RAM (subset) → features → disk
Later runs: Disk → RAM (small tables only)
```

---

## 3. Features (19 numbers per page)

From `src/features.py` — hand-crafted, no full HTML text in the model.

**URL (12):** length, host/path length, dots, hyphens, digits, subdomains, HTTPS, `@`, IP host, suspicious tokens (`login`, `bank`, …).

**HTML (7):** length, forms, inputs, password fields, scripts, links, iframes.

**Labels:** `1` = phishing, `0` = benign.

---

## 4. Algorithms we used

### Logistic Regression (linear baseline)

```
StandardScaler → LogisticRegression(class_weight='balanced', max_iter=1000)
```

- Learns a **weighted sum** of features → probability of phishing.
- Needs scaling; fast and interpretable.
- Weaker on this task at 1% prevalence (precision ~0.06).

### Random Forest (main model)

```
StandardScaler → RandomForestClassifier(n_estimators=200, class_weight='balanced')
```

- **200 decision trees** vote; captures non-linear patterns.
- Best model in our project (F1 0.91 on test, 0.66 at 1%).

**`class_weight='balanced'`:** Penalizes errors on the minority class so the model does not ignore phishing or benign.

**Train:** 5,000 rows (~44% phishing). **Test:** 1,000 rows (~45% phishing).

---

## 5. Confusion matrix (foundation of all metrics)

```
                        Predicted
                     Benign    Phishing
Actually Benign       TN        FP   ← false alarm (block innocent site)
Actually Phishing     FN        TP   ← missed attack
```

**Our Random Forest on test set:** 31 FP, 53 FN.

---

## 6. Metrics — short definitions

| Metric | Question | Formula idea |
|--------|----------|--------------|
| **Precision** | Of pages we **blocked**, how many were truly phishing? | TP / (TP + FP) |
| **Recall** | Of **real** phishing, how many did we **catch**? | TP / (TP + FN) |
| **Accuracy** | Overall % correct | (TP + TN) / all |
| **F1** | Balance of precision and recall | 2 × P×R / (P + R) |
| **MCC** | Fair single score when classes are imbalanced | Uses all four cells |
| **ROC-AUC** | Can model **rank** phishing above benign? | 0.5 = random, 1.0 = perfect ranking |

### Phishing meaning

- **Low precision** → too many **false positives** (innocent sites blocked) → users lose trust.
- **Low recall** → too many **false negatives** (attacks missed) → fraud reaches users.
- **High ROC-AUC** → model **scores** phishing higher than benign, even if threshold 0.5 is wrong for deployment.

### Memory tricks

- **Precision** → “Were our **warnings** correct?”
- **Recall** → “Did we **catch the attacks**?”
- **ROC-AUC** → “Can we **sort** phishing above benign?” (threshold-independent)

---

## 7. Our Random Forest results

| Metric | ~45% test | ~1% benchmark | Inflated at high prevalence? |
|--------|-----------|---------------|------------------------------|
| Precision | **0.928** | **0.508** | **Yes** |
| F1 | **0.905** | **0.660** | **Yes** |
| Recall | 0.883 | 0.941 | No |
| ROC-AUC | 0.974 | ~0.99 | No |
| Accuracy | 0.916 | — | Often misleading when rare |

**Prevalence sweep (RF):** Precision rises from ~51% (1%) to ~93% (25–45%) as phishing gets more common in the evaluation set.

---

## 8. Precision drop = more innocent blocks (FP)

When precision dropped from **0.93 → 0.51**:

- We still **catch** most phishing (**recall** stayed high).
- Among pages we **flagged**, a **much larger share** were innocents.
- At ~45% test: ~**7%** of blocks were wrong (FP).
- At ~1%: ~**49%** of blocks were wrong (FP).

**Important:** Absolute FP count can be **similar** (~31). Precision drops because there are **fewer true phishing among our blocks** when phishing is rare — same alert level, worse mix.

**One line:** Precision dropped because **false positives made up a much larger fraction of our blocks** when phishing was rare.

---

## 9. What “inflated metrics” means

**Not** that we cheated or the model is fake.

It means: headline **precision/F1 on a 45% test** look **deployment-ready**, but the **same model** at **1%** tells a much worse **false-alarm** story.

- **Inflated:** precision, F1 (and accuracy can mislead).
- **Stable:** ROC-AUC (ranking), recall (at our threshold).

---

## 10. PhreshPhish claims (context)

| Claim | Meaning | We tested? |
|-------|---------|------------|
| Old data has leakage + low quality | Train/test overlap, bad labels inflate scores | No |
| Unrealistic base rate inflates precision/F1 | 50% phish in test ≠ real world | **Yes** |
| PhreshPhish benchmarks are rigorous | Official 975 sets with filters + low rates | Partially (our own 1% sim) |

---

## 11. Exam / oral one-liners

**Project in one sentence:**  
We reproduced a phishing detector on a PhreshPhish subset and showed that precision falls from 0.93 to 0.51 when evaluation prevalence drops from ~45% to ~1%, supporting the paper’s base-rate argument.

**Metrics in one sentence:**  
At 1% phishing the model still ranks well (high ROC-AUC) and catches most attacks (high recall), but blocking at threshold 0.5 means about half of blocked pages are innocent (low precision).

**Data in one sentence:**  
We stream a subset from Hugging Face with HTML capped for RAM, extract 19 features, and cache parquet on disk for fast re-runs.

---

## 12. Key config (notebook cell 1)

```python
TRAIN_SAMPLE_SIZE = 5_000
TEST_SAMPLE_SIZE = 1_000
MAX_HTML_CHARS = 80_000
LOW_BASE_RATE = 0.01
FORCE_REBUILD_CACHE = False
```

---

*See also: `notebooks/phreshphish_analysis.ipynb`, `report/phreshphish_final_report.pdf`*
