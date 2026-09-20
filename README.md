<div align="center">

  <img src="assets/BudgetWise_AI_logo.png" alt="BudgetWise AI Logo" width="120" height="120" />

# BudgetWise AI v2.2.0 (Windows Standalone App release)
  
  **Cross-Platform Financial Intelligence & Statutory Governance Engine for International Students**

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

**BudgetWise AI** is a multi-platform financial intelligence and predictive budget-planning system built in Python, tailored specifically for international students studying abroad to manage cross-border currency exposure, statutory wage compliance, tax withholdings, and solvency runways[cite: 3].

Available natively on desktop via PyQt5 and mobile via Flet / Flutter, underpinned by a fault-tolerant microservice inference API deployed on Render[cite: 3].

---

## ✨ Core Features

* **Cross-Jurisdictional Statutory Engine:** Ingests dynamic regulatory criteria (`COUNTRY_NAME`, `COUNTRY_WAGE`, `COUNTRY_WORK_RATE`) via the REST Countries v3.1 API and live foreign exchange (FX) feeds to compute legal minimum wage floors and visa work-hour limitations automatically[cite: 3].
* **Algorithmic Tax & Fortnight Expenditure Analytics:** Models non-linear tax withholdings through a continuous logistic curve parameterized by relative logarithmic wage-differentials ($D$)[cite: 3].
* **Automated Transaction Categorization Pipeline:** Multi-class classification engine leveraging Scikit-Learn pipelines and Naive Bayes inference to map unstructured transaction payloads into standardized budgetary sectors[cite: 3].
* **Bifurcated Product Affordability Engine:** Evaluates prospective acquisitions against a 180-day empirical expenditure curve[cite: 6]. Micro-purchases (< $2,000 AUD) are assessed against weekly liquidity burn and dynamic SafeSpend degradation; macro acquisitions ($\ge$ $2,000 AUD) verify structural preservation of a 6-week baseline capital runway[cite: 6].
* **Tamper-Evident `.rcd` Archive Container:** Proprietary weekly binary ledger format featuring a 5-byte magic signature (`BWRCD`), an authoritative 32-byte SHA-256 cryptographic digest, and Gzip-compressed UTF-8 JSON payloads for verifiable data portability[cite: 3, 7].
* **Ordinary Least Squares (OLS) Velocity Forecasting:** Dynamic linear regression engine modeling fortnightly expenditure curves, velocity trajectories, and runway solvency risks[cite: 3].
* **SafeSpend™ Dynamic Liquidity Allocator:** Algorithmic daily capital bounds factoring remaining semester horizons, fixed overhead amortization, and historical burn rates[cite: 3].
* **Multi-Platform Deployment Architecture:**
  * **Desktop:** Standalone, single-file Windows PE binary (`.exe`) compiled via PyInstaller with bundled scikit-learn models and runtime asset resolvers[cite: 3].
  * **Mobile:** Android APK compiled via Flutter runtime and the Serious Python bridge[cite: 3].
  * **Cloud Infrastructure:** Asynchronous FastAPI service on Render providing OpenAPI/Swagger specs and stateless inference endpoints[cite: 3].

---

## 🚀 Technologies & Libraries

* **Core Language:** Python 3.11+[cite: 3]
* **User Interfaces:** PyQt5 (Desktop), Flet / Flutter (Mobile & PWA)[cite: 3]
* **Backend Framework:** FastAPI, Uvicorn, Pydantic[cite: 3]
* **Machine Learning & Analytics:** Scikit-Learn, NumPy, Pandas, Joblib[cite: 3]
* **Data Serialization & Cryptography:** Gzip compression, Hashlib (SHA-256), Custom Binary Stream Structs (`.rcd`)[cite: 3]
* **Data Visualization:** Matplotlib[cite: 3]
* **External APIs:** Gemini API, REST Countries v3.1, Open Exchange Rates[cite: 3]
* **Packaging & Tooling:** PyInstaller, Winreg Shell Integration, GitHub Actions, Android NDK[cite: 3]

---

## 📝 Changelogs

### v2.2.0 (Latest Release)
* **Portable Binary Deployment & Frozen Environment Hardening:**
  * Re-architected desktop packaging to a zero-dependency, single-file executable (`--onefile`, `--windowed`) using a declarative PyInstaller `.spec` manifest.
  * Implemented `get_resource_path()` using `getattr(sys, "_MEIPASS", ...)` fallback mechanics to ensure deterministic resolution of logos, textures, and serialized models from isolated extraction environments.
  * Eliminated runtime DLL loader failures (`python313.dll`) by ensuring monolithic bundling of the CPython runtime, PyQt5 bindings, and C-extension binaries (`sklearn.utils._typedefs`).
  * Purged heavy build artifacts (`dist/`, `build/`, `.pkg`) from the Git tree and instituted strict `.gitignore` rules to stay compliant with upstream remote push limits.
* **Standalone `.rcd` Decompiler & Operating System Shell Association:**
  * Created `RCDViewerWindow`: a standalone GUI viewer that parses `.rcd` binary streams, performs cryptographic hash validation, and dynamically renders ledger entries and summary metrics without launching the core application.
  * Added bidirectional transcoding, allowing non-technical users to decompile verified `.rcd` archives directly to structured JSON or RFC 4180 CSV formats.
  * Developed a user-space Windows Shell registry injector (`setup_open_with.py`) mapping the `.rcd` file extension and `BudgetWise.RCDViewer.1` ProgID directly to the compiled executable via standard OS command protocols (`"%1"`).
  * Built working-directory invariant path resolution (`os.chdir(PROJECT_ROOT)`) ensuring shell-launched `.rcd` files correctly deserialize independent of parent process invocation paths.
* **Data Layer & Workspace Decoupling:**
  * Refactored `pages/reports.py` and `main.py` interfaces, eliminating class-attribute resolution conflicts (`back_btn`, `set_user_context`, `update_report`) and eradicating cross-version PyQt5/PyQt6 binding collisions.
  * Connected runtime export paths directly to `UserDataManager`, enabling dynamic, user-configured filesystem targets for financial archives.

### v2.1.0
* **Added Product Affordability Analyzer:**
  * Integrated an interactive slide-out panel (`AffordabilityChatPanel`) into the primary desktop layout with dynamic UI signal toggles[cite: 6].
  * Structured mathematical spending verifications across a Micro-velocity engine (< $2,000 AUD) and Macro Capital Runway checks ($\ge$ $2,000 AUD)[cite: 6].
  * Built regex-driven natural language query tokenizers extracting currency values, currencies (AUD, USD, bucks), and product semantics[cite: 6].
  * Incorporated student labor opportunity cost metrics calculated against statutory hourly wage baselines[cite: 6].
* **Engine Architecture & Cloud API Updates:**
  * Integrated the `/api/v1/affordability/analyze` route into the FastAPI web platform.
  * Added offline random forest classifier training routines (`models/train_affordability.py`).
  * Upgraded `FinancialReportPage` with weekly range filtering and direct `.rcd` archive packing[cite: 7].

### v2.0.0
* Migrated cloud backend architecture to FastAPI with OpenAPI documentation[cite: 3].
* Integrated Ordinary Least Squares (OLS) regression models for fortnightly trajectory forecasting[cite: 3].
* Implemented statutory student visa work condition validations (Subclass 500 fortnightly work-hour caps)[cite: 3].

---

## 🛠️ Installation & Local Setup

### Prerequisites

* Python 3.11 or higher[cite: 3]
* Git[cite: 3]
* pip 24.0+

### Step 1: Clone Repository & Initialize Environment

```bash
git clone [https://github.com/specrthyahskod/BudgetWise-AI.git](https://github.com/specrthyahskod/BudgetWise-AI.git)
cd BudgetWise-AI

# Create and activate virtual environment
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

# Run desktop client from source
python main.py

# Compile standalone Windows binary via specfile
pyinstaller --noconfirm build_config.spec
