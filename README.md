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
