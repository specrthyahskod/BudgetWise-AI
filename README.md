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
* **SafeSpend™ Dynamic Daily Limits:** Algorithmic liquidity allocator factoring semester runway timelines, fixed overheads, and weekly burn rates.
* **Multi-Platform Deployment Architecture:**
  * **Desktop:** Native standalone Windows binary (`.exe`) compiled via PyInstaller with bundled ML models.
  * **Mobile:** High-performance Android application (`.apk`) leveraging hardware-accelerated Flutter rendering.
  * **Cloud Services:** FastAPI web service deployed on Render providing microservice inference and interactive OpenAPI documentation.

---

## 🚀 Technologies & Libraries

* **Core Language:** Python 3.11+
* **User Interfaces:** PyQt5 (Desktop), Flet / Flutter (Mobile & PWA)
* **Backend Framework:** FastAPI, Uvicorn, Pydantic
* **Machine Learning & Analytics:** Scikit-Learn, NumPy, Pandas, Joblib
* **Data Visualization:** Matplotlib
* **External APIs:** Gemini API, REST Countries v3.1, Open ER Foreign Exchange
* **Packaging & CI/CD:** PyInstaller, GitHub Actions, Android SDK / Serious Python

---

## 🛠️ Installation & Local Setup

### Prerequisites

* Python 3.11 or higher
* Git

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

---

###Installion of python libraries and packages
pip install --upgrade pip
pip install -r requirements.txt
