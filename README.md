# 🕵️ Dark Pattern Detector

A machine learning–powered tool to detect deceptive UX patterns in Indian e-commerce product listings (Amazon, Flipkart, etc.).

## 🔍 What It Detects

| Pattern | Description | Severity |
|---|---|---|
| ⏰ Urgency & Scarcity | "Only 2 left!", fake countdown timers | High |
| 💸 Misleading Discounts | Inflated MRP, fake % off | High |
| 👥 Social Proof Manipulation | "142 people viewing", fake bestseller badges | Medium |
| 🔍 Hidden Costs | Platform fees, packaging charges revealed late | High |
| 😔 Confirm Shaming | "No thanks, I don't want to save money" | Medium |
| 🛒 Basket Sneaking | Pre-selected warranty/subscription add-ons | High |
| 📢 Disguised Ads | Sponsored listings styled as organic results | Low |
| ❓ Trick Questions | Double-negative opt-out checkboxes | Medium |

## 🚀 Running Locally

```bash
git clone https://github.com/yourusername/dark-pattern-detector
cd dark-pattern-detector
pip install -r requirements.txt
streamlit run app.py
```

## 🛠️ Tech Stack

- **Python** — Core language
- **Scikit-learn** — TF-IDF + Logistic Regression classifier
- **NLTK / Regex** — Rule-based pattern matching
- **BeautifulSoup4** — Web scraping
- **Streamlit** — Dashboard UI
- **Plotly** — Interactive visualizations
- **Pandas** — Data handling and CSV export

## 🏗️ Architecture

```
Input (URL / Pasted Text)
       │
       ▼
  Scraper (BeautifulSoup)
       │
       ▼
  Text Preprocessor
       │
   ┌───┴───┐
   │       │
Rule-    ML Model
Based    (TF-IDF +
Regex    LogReg)
   │       │
   └───┬───┘
       │  Merge & Deduplicate
       ▼
  Deception Score (0–100)
       │
       ▼
  Plotly Dashboard + CSV Export
```

## 📊 Deception Score

| Score | Verdict |
|---|---|
| 0 | ✅ Clean |
| 1–20 | 🟡 Mildly Deceptive |
| 21–50 | 🟠 Moderately Deceptive |
| 51–100 | 🔴 Highly Deceptive |

Scores are weighted by severity: High (15pts), Medium (8pts), Low (3pts), capped at 100.

## 💡 Motivation

India's CCPA (Consumer Protection Act) recognizes dark patterns as an unfair trade practice. This tool was built to raise awareness and provide a practical way to audit e-commerce listings for consumer-hostile design.

## 📁 Project Structure

```
dark-pattern-detector/
├── app.py           # Streamlit frontend
├── detector.py      # ML + rule-based detection engine
├── scraper.py       # Web scraper + demo samples
├── requirements.txt
└── README.md
```

## 🔗 Deploy on Streamlit Cloud

1. Push to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set `app.py` as entrypoint → Deploy

---
Built by Sahil Rai | [raisahil909@gmail.com](mailto:raisahil909@gmail.com)
