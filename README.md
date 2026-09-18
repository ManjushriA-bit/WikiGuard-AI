# 🛡️ WikiGuard AI — Challenge 4

> **An evidence-first fact-consistency checker for Wikimedia Structured Contents**

WikiGuard AI is a working prototype for **Challenge 4 — WikiFact Check**. It loads a Wikimedia Structured Wikipedia Dataset Parquet shard through Kaggle/KaggleHub, extracts structured facts, searches article text for supporting evidence, normalizes values, and flags cases that need human verification.

## ⚠️ Important principle

WikiGuard AI does **not** say that a Wikipedia fact is false.

> **Possible mismatch detected — human verification recommended.**

The tool is an investigation aid: it presents the structured value, the article value/evidence, and the reason for the flag.

## 🌟 Key features

- 🔎 Search and select an article from the Wikimedia dataset
- 📦 Extract structured/infobox facts
- 📄 Build searchable article text from description, abstract and sections
- 🧹 Normalize dates, punctuation, whitespace and common country-name aliases
- 🧠 Compare structured values against article evidence
- ⚠️ Detect possible date/value mismatches
- 🕵️ Show an evidence window around the matching text
- 📊 Produce an investigation summary
- 🧪 Include a deterministic demonstration record for testing the comparison engine
- 🧩 Keep the comparison engine separate in wikiguard_core.py

## 🔄 System flow

Kaggle Wikimedia Structured Contents → Load Parquet → Search Article → Select Record → Extract Structured Facts → Read Article Text → Normalize Values → Compare Evidence → Consistent / Possible Mismatch / Not Found → Evidence Window → Human Verification

## 🛠️ Technology stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Pandas | Wikimedia dataset processing |
| NumPy | Data handling |
| scikit-learn | NLP/similarity extension point |
| PyArrow | Parquet support |
| KaggleHub | Loading the Kaggle dataset |
| Google Colab | Reproducible execution |

## 📦 Dataset

The project uses the **Wikimedia Foundation — Wikipedia Structured Contents** dataset available through Kaggle.

Configured example shard:

    wikimedia-foundation/wikipedia-structured-contents
    enwiki/data/enwiki_namespace_0_00008.parquet

The shard path can be changed in one configuration cell if another English Wikipedia shard is preferred.

The repository does not store the large Parquet dataset or Kaggle credentials.

## ▶️ Run the project

### Google Colab

Open **WikiFact_Check_WikiGuard_AI.ipynb** and run the notebook from top to bottom.

The notebook installs dependencies, loads the Wikimedia Parquet shard with KaggleHub, displays the real row/column information, searches loaded articles, extracts structured facts, runs the comparison engine, displays investigation cards and a final report, and runs a clearly labelled deterministic demonstration so the mismatch workflow is reproducible even when a live article has sparse infobox data.

### Local

    pip install -r requirements.txt
    jupyter notebook

## 🧠 Detection logic

1. Read the infoboxes field.
2. Parse nested JSON/Python-like structures.
3. Flatten nested key/value pairs.
4. Combine description, abstract and sections into article text.
5. Search for the structured value.
6. Normalize both sides.
7. Treat exact/normalized evidence as CONSISTENT.
8. For date-like fields, detect dates in the article and compare normalized dates.
9. If a different date/value is detected, return POSSIBLE MISMATCH.
10. Show an evidence window so a person can inspect the context.

## 🕵️ Fact Investigation Card

Each result answers four questions quickly:

**What was the structured fact?** The value stored in the structured Wikimedia record.

**What did the article text say?** The matching or conflicting value found in the article text.

**Why was it flagged?** Because the normalized structured value and article evidence did not agree.

**What should happen next?** Human verification.

## 📊 Example output

    ============================================================
    🛡️ WIKIGUARD AI — FACT INVESTIGATION
    ============================================================

    Article: Demo Person

    FACT 1
    Structured value : 12 March 1988
    Article evidence  : 14 March 1988
    Status            : ⚠️ POSSIBLE MISMATCH

    Evidence:
    ...the article states that Demo Person was born on
    14 March 1988 in...

    Recommendation:
    Human verification recommended.

## 📁 Repository structure

    WikiGuard-AI/
    ├── README.md
    ├── requirements.txt
    ├── .gitignore
    ├── wikiguard_core.py
    ├── WikiFact_Check_WikiGuard_AI.ipynb
    └── screenshots/
        ├── 01_dataset_and_search.svg
        ├── 02_fact_extraction.svg
        ├── 03_possible_mismatch.svg
        └── 04_final_report.svg

## 🔐 Security

Never commit Kaggle credentials, API tokens, downloaded Parquet files, passwords or private credentials. Large dataset files are intentionally excluded with .gitignore.

## 🚀 Future scope

- Named Entity Recognition
- sentence-level semantic similarity
- stronger numeric and unit normalization
- multilingual fact comparison
- confidence explanations
- revision-aware Wikipedia comparison
- interactive web dashboard
- exportable verification reports
- batch scanning of large article collections

## 📌 Status

**Challenge 4 — WikiFact Check: WikiGuard AI prototype ✅**

Built as a structured, evidence-first solution for the Wikimedia Structured Wikipedia Dataset hands-on project.
