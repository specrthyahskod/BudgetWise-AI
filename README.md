<div align="center">

  <img src="assets/BudgetWise_AI_logo.png" alt="BudgetWise AI Logo" width="120" height="120" />

# BudgetWise AI
  
  **Cross Platform Financial Assistant Monitior for International students studying abroad**

  [![FastAPI Status](https://img.shields.io/badge/API-FastAPI%200.110+-009688.svg?style=flat&logo=fastapi)](https://budgetwise-ai-mobile.onrender.com/docs)
  [![Flutter / Flet Engine](https://img.shields.io/badge/UI-Flet%200.86+-02569B.svg?style=flat&logo=flutter)](https://flet.dev)
  [![Build Status](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg?style=flat&logo=githubactions)](https://github.com)
  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python)](https://python.org)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

  [Live BudgetWiseAI Financial Model API](https://budgetwise-ai-o4xs.onrender.com)
  [BudgetWise AI API Documentation](https://budgetwise-ai-o4xs.onrender.com/docs)  

</div>

---

## 📌 Overview

**BudgetWise AI** is a multi-platform financial intelligence and predictive budget-planning system built in Python, tailored specifically for international students studying abroad helping to manage their their finances, wages, taxes and savings.

Available on desktop via (PyQt5) and native mobile deployment via (Flet / Flutter) with a fault-tolerant cloud API (Render).

---

## ✨ Core Features

* **Cross-Jurisdictional Statutory Engine:** Country meta data like COUNTRY_NAME, COUNTRY_WAGE, COUNTRY_WORK_RATE etc are fetched via the REST Countries API, paired with live foreign exchange (FX) feeds to find legal wage minimums and statutory visa work limitations automatically.
* **Algorithmic Tax & Fortnight Expenditure Analytics:** Replaces arbitrary income tax estimates with a continuous logistic withholding curve and relative logarithmic wage-differential metrics ($D$).
* **Automatic Transaction Categorizer:** Real-time Naive Bayes / Scikit-Learn pipeline trained to classify unstructured transaction payloads into standardized budget sectors instantly.
* **Product Affordability Analyzer (Macro Burn & Micro Curve Engine):** Evaluates ad-hoc product purchases against historical 180-day spending velocity. Micro-purchases (<$2,000 AUD) are tested against current-week velocity and daily SafeSpend degradation, while macro acquisitions (≥$2,000 AUD) verify preservation of a 6-week emergency runway reserve.
* **Tamper-Evident `.rcd` Financial Archive Container:** Proprietary weekly binary ledger export format utilizing a 5-byte magic signature (`BWRCD`), 32-byte SHA-256 integrity checksum, and Gzip-compressed UTF-8 payloads for verifiable cross-client data portability[cite: 3].
* **Ordinary Least Squares (OLS) Velocity Forecasting:** Dynamic linear regression engine forecasting fortnight trajectory burn rates and solvency risk metrics[cite: 2].
* **SafeSpend™ Dynamic Daily Limits:** Algorithmic liquidity allocator factoring semester runway timelines, fixed overheads, and weekly burn rates.
* **Multi-Platform Deployment Architecture:**
  * **Desktop:** Native standalone Windows binary (`.exe`) compiled via PyInstaller with bundled ML models.
  * **Mobile:** High-performance Android application (`.apk`) leveraging hardware-accelerated Flutter rendering.
  * **Cloud Services:** FastAPI web service deployed on Render providing microservice inference and interactive OpenAPI documentation.

---

## 🚀 Technologies & Libraries:-

* **Core Language:** Python 3.11+
* **User Interfaces:** PyQt5 (Desktop), Flet / Flutter (Mobile & PWA)
* **Backend Framework:** FastAPI, Uvicorn, Pydantic
* **Machine Learning & Analytics:** Scikit-Learn, NumPy, Pandas, Joblib and REST API
* **Data Packaging & Compression:** Gzip, Hashlib (SHA-256), Custom Binary Serialization (`.rcd`)[cite: 3]
* **Data Visualization:** Matplotlib
* **External APIs:** Gemini API, REST Countries v3.1, Open ER Foreign Exchange
* **Packaging & CI/CD:** PyInstaller, GitHub Actions, Android SDK / Serious Python

---

## 📝 Changelogs:-

### v2.1.0 (Latest Release)
* **Added Product Affordability Analyzer:**
  * Integrated an interactive slide-out AI assistant into the desktop layout and public web API.
  * Bifurcated spending models into a Micro-velocity engine (<$2,000 AUD) and Macro Capital Runway checks (≥$2,000 AUD).
  * Natural language query parser with automatic regex-driven price and item extraction.
  * Added shift/labor opportunity cost metrics computed from net hourly wages.
* **Added Custom `.rcd` Weekly Archive Format:**
  * Introduced native binary packing and unpacking via `models/rcd_format.py`[cite: 3].
  * Added cryptographic data integrity verification using 32-byte SHA-256 hash validation before gzip payload decompression[cite: 3].
  * Upgraded `FinancialReportPage` with weekly ledger filtering, real-time metrics generation, and direct `.rcd` file export[cite: 7].
* **Engine Architecture & Cloud API Enhancements:**
  * Integrated the `/api/v1/affordability/analyze` route into the FastAPI web platform.
  * Added Scikit-Learn random forest affordability risk classifier training scripts (`models/train_affordability.py`).
  * Reconciled PyQt5 UI layouts, resolving language server caching errors and workspace module conflicts[cite: 1, 7].

### v2.0.0
* Re-engineered cloud API with FastAPI, supporting live Swagger/OpenAPI documentation[cite: 2].
* Integrated Ordinary Least Squares (OLS) fortnightly burn-rate regression forecasting[cite: 2].
* Implemented cross-jurisdiction student visa compliance checks (subclass 500 fort-nightly work caps)[cite: 2].

---

## 🛠️ Installation & Local Setup

### Prerequisites:-

* Python 3.11 or higher
* Git
* pip 26.2.1

### Step 1: Clone Repository & Initialize Environment

```bash
git clone [https://github.com/your-username/BudgetWise-AI.git](https://github.com/your-username/BudgetWise-AI.git)
cd BudgetWise-AI

# Create and activate virtual environment
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate