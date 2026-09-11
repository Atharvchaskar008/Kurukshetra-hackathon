# SupplyGuard

> Intelligent Software Supply Chain Security & Dependency Risk Analysis Platform

SupplyGuard is an automated security platform designed to analyze dependencies, detect software supply chain risks, uncover malicious packages, typosquatting, and vulnerable transitive dependencies across multiple ecosystems.

---

## 📁 Repository Structure

```text
├── backend/            # Backend API services, detectors, analysis pipelines, models
├── frontend/           # Web interface & dashboard for vulnerability visualization
├── tests/              # Unit, integration, and end-to-end tests
├── demo-repository/    # Sample vulnerable / test repositories for simulation & analysis
├── scripts/            # Automation, setup, benchmarking, and helper scripts
├── docs/               # Architecture design, API specs, and technical documentation
├── .env.example        # Environment variable configuration template
├── .gitignore          # Git ignore rules for Python, Node, environment files
└── README.md           # Project documentation and getting started guide
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend dashboard)
- Git

### Initial Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Configure your environment variables in `.env`.
3. Create a virtual environment and install Python dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Run the backend:
   ```bash
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```
5. Open http://127.0.0.1:8000/health and http://127.0.0.1:8000/docs

Run tests from the repository root:

```bash
python -m pytest
```

Firebase is optional. If credentials are unset, scans persist in memory for the process lifetime.

The frontend dashboard is not wired yet (see `IMPLEMENTATION_PLAN.md` and `NEXT_25_PROMPTS.md`).
