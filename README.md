# 📘 Street Vendor Demand Predictor (SVDP)

An AI-powered agent designed to help small food vendors in India forecast daily demand, optimize inventory, and improve profitability — all within local context.

---

## 👤 Author

**Kumar Kshitij**
*Business Growth Analyst – AI Agent Assignment*

---

## 🧠 Problem Statement

Most AI solutions ignore the informal economy. This project bridges that gap by building a conversational agent that understands food cart vendors' real-world constraints — weather, footfall, pricing, and leftovers — in rupees and paise.

---

## 🎯 Goal

Help Indian street vendors answer:
"*Kitna maal laaun aaj ke liye?*" — using real data and rupee-focused prediction.

---

## 🛠️ Architecture (4 Layers)

1. **Input Layer**: Converts natural language and structured data into normalized vendor context.
2. **State Layer**: Maintains memory (`memory.json`) of each vendor, sales patterns, and heuristics.
3. **Task Layer**: Performs demand prediction, risk/opportunity analysis.
4. **Output Layer**: Returns actionable advice in simple Hinglish, includes peak hours, expected revenue, and tips.

---

## 🗂️ File Structure

```
svdp/
├── agent.py                  # Main AI logic (all 4 layers)
├── memory.json               # Stores vendor history and patterns
├── prompts/
│   └── prompt_templates.txt  # (Optional) Prompt templates
├── data/
│   └── sample_vendors.csv    # Sample vendor data (for UI loading)
├── ui/
│   └── terminal_ui.py        # CLI for selecting vendor, running predictions
├── logs/
│   └── logbook_2025-06-16.md # Development diary with breakthroughs
└── README.md                 # This file
```

---

## 🚀 How to Run

### 1. Setup

Make sure you're in a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
```

### 2. Run the CLI

```bash
python ui/terminal_ui.py
```

---

## 🧪 Features

* Realistic demand estimation using context: day, temperature, weather, festival
* Bilingual-friendly responses with rupee figures
* Confidence score based on memory length
* Dynamic memory updating after every prediction

---

## 📅 Project Timeline

| Phase   | Deliverable                           | Deadline      |
| ------- | ------------------------------------- | ------------- |
| Phase 1 | Core agent + data structure           | ✅ June 16     |
| Phase 2 | Testing all 4 layers, vendor profiles | June 26       |
| Phase 3 | Polish, logs, final batch testing     | July 18, 7 PM |


### 🌐 Run the Web UI

Make sure you're in your virtual environment and have Flask installed:

```bash
pip install flask
```

Then start the web version of the predictor:

```bash
python ui/web_ui.py
```

Open your browser and go to:

```
http://127.0.0.1:5000
```

Use the form to select a vendor, fill in weather and day details, and view a prediction summary including inventory advice and special notes.

---
---

## 📬 Contact

For any queries or testing requests: `kumar.kshitij@proton.me`

