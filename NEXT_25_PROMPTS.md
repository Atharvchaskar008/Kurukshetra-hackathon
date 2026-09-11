# Next 25 Implementation Prompts

These continue from the **actual** repo (ecosystem detection + ZIP upload + Git cloner + empty frontend). They are **not** a replay of original 01–25.

Do not rebuild FastAPI, Firestore fallback, ZIP extractor, GitCloner, or ecosystem detection.

---

## Prompt 26 — Backend runtime bootstrap

### Objective

Make the backend installable and testable on a clean machine.

### Why

There is no root `requirements.txt` / pytest config. The app cannot be demonstrated if dependencies are implicit.

### Implementation

- Add `requirements.txt` with: `fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `python-multipart`, `httpx`, `pytest`.
- Add `pytest.ini` with `pythonpath = .` and `testpaths = tests`.
- Add `GROK_API_KEY=` to `.env.example` (config already reads it).
- Document in README: copy `.env.example` → `.env`, `pip install -r requirements.txt`, `python -m uvicorn backend.main:app --reload`.
- Do not add scanners, frontend, or orchestrator in this commit.

### Files likely affected

- `requirements.txt`
- `pytest.ini`
- `.env.example`
- `README.md` / `readme.md`

### Verification

- `python -c "import fastapi, pydantic"` after install
- `python -m pytest tests/test_health.py tests/test_api_schemas.py -q`

### Completion criteria

- Fresh venv can install and import the backend
- Health tests pass

### Git commit

`feat(26): add backend runtime dependencies and pytest config`

---

## Prompt 27 — Land static package.json parser

### Objective

Commit the existing untracked `backend/parsers` package.json parser and keep tests.

### Why

Node declared-dependency extraction is already written locally but not in git and not part of the scan pipeline yet.

### Implementation

- Keep `parse_package_json`, `parse_package_json_file`, `parse_nested_package_jsons`, `parse_workspace_package_jsons`.
- Ensure JSON-only parsing; never call npm; preserve ranges; malformed JSON returns `parse_ok=False`.
- Do not parse `package-lock.json`.
- Do not wire the orchestrator yet unless already trivial.

### Files likely affected

- `backend/parsers/*`
- `tests/test_package_json_parser.py`

### Verification

- `python -m pytest tests/test_package_json_parser.py -q`

### Completion criteria

- Parser is in git
- Tests cover normal, all sections, malformed, empty, nested

### Git commit

`feat(27): add static package.json dependency parser`

---

## Prompt 28 — Static Python declared-dependency parser

### Objective

Parse `requirements.txt` and a minimal `pyproject.toml` `[project.dependencies]` list without executing pip/python from the repo.

### Why

Ecosystem detection already finds Python manifests; declared deps are not extracted. Demo will likely include npm + pip.

### Implementation

- Add `backend/parsers/requirements_txt.py` (PEP 508 name + specifier preserved exactly).
- Skip comments, blanks, `-r`, `-e`, `--hash` lines without executing them.
- Add minimal TOML scan for `pyproject.toml` project.dependencies using stdlib `tomllib` (3.11+) or a tiny fallback; never exec `setup.py`.
- Map to existing `DeclaredDependency` / `Dependency` with `ecosystem=pypi`.
- Malformed lines skipped, file still succeeds.

### Files likely affected

- `backend/parsers/requirements_txt.py`
- `backend/parsers/pyproject.py`
- `backend/parsers/__init__.py`
- `tests/test_python_parsers.py`

### Verification

- Fixtures under `tests/fixtures/ecosystems/python_project/`
- No `subprocess` to pip

### Completion criteria

- requirements.txt + pyproject dependencies extracted with exact specifiers

### Git commit

`feat(28): parse Python requirements and pyproject dependencies statically`

---

## Prompt 29 — Scan orchestrator skeleton

### Objective

Run a deterministic pipeline on an existing `RepositoryWorkspace`: detect ecosystems → parse package.json + Python manifests → persist dependencies and inventory on the scan document → set status COMPLETED or FAILED.

### Why

ZIP upload currently stops at PENDING. Nothing analyzes the tree.

### Implementation

- Add `backend/pipeline/orchestrator.py` with `run_scan(scan_id, workspace, repository)`.
- Stages: `ingested` → `ecosystems` → `dependencies` → `completed`.
- Persist on scan: `ecosystems_detected`, `manifest_inventory` summary, `dependencies` list, `stage_status`, `error_message`.
- Use in-memory `ScanRepository`; do not require Firebase.
- Never run npm/pip/setup.py/syft/grype in this commit.
- Store `workspace_path` on the scan only if still needed; prefer finishing before workspace cleanup.

### Files likely affected

- `backend/pipeline/orchestrator.py`
- `backend/pipeline/__init__.py`
- `backend/database/repository.py` (only if extra fields needed)
- `tests/test_orchestrator.py`

### Verification

- tmp workspace with package.json → scan has declared deps
- empty unknown repo → completed with zero deps, not crash

### Completion criteria

- Orchestrator produces persisted dependencies without network

### Git commit

`feat(29): add scan orchestrator for ecosystem and dependency extraction`

---

## Prompt 30 — GitHub scan create endpoint

### Objective

Add `POST /api/v1/scans/github` that validates URL, clones with existing `GitCloner`, creates scan, runs orchestrator.

### Why

`GitHubScanRequest` and `GitCloner` exist but are unused by the API.

### Implementation

- Router uses `GitHubScanRequest`.
- Validate via `validate_github_url`.
- Clone with timeout; map clone failures to existing `RepositoryIngestionError`.
- Return `ScanCreateResponse` with `scan_id`.
- Run orchestrator synchronously for demo reliability (document timeout: `SCAN_TIMEOUT_SECONDS`).
- Cleanup workspace in `finally`.

### Files likely affected

- `backend/routers/scans.py`
- `tests/test_github_scan_api.py`

### Verification

- Mock `GitCloner.clone` to a tmp workspace; POST returns 200 + scan_id
- Invalid URL returns 400/422 via existing handlers
- Assert git clone is not given a shell string

### Completion criteria

- GitHub scan API creates a scan and fills dependencies when clone succeeds

### Git commit

`feat(30): add GitHub repository scan API endpoint`

---

## Prompt 31 — Scan status and detail retrieval

### Objective

Add `GET /api/v1/scans/{scan_id}` (status) and `GET /api/v1/scans/{scan_id}/details` using existing `ScanStatusResponse` and `ScanDetailResponse`.

### Why

Frontend and demo cannot poll or show results. Upload/GitHub create cannot be observed.

### Implementation

- Status: `status`, `progress_percent` (derive from stage), `current_stage`, `error_message`.
- Details: repository metadata, dependencies (`DependencyResponse`), empty findings/risk/graph until later prompts.
- 404 via existing not-found exception if missing.
- Wire ZIP upload to call orchestrator before response **or** immediately after persist (same process). Prefer completed scans for demo.

### Files likely affected

- `backend/routers/scans.py`
- `backend/schemas/scan.py` (only if a field is missing)
- `tests/test_scan_retrieval.py`

### Verification

- Upload ZIP fixture npm_project → GET details lists `express` (or fixture dep) with exact range

### Completion criteria

- Status + details work for ZIP and (mocked) GitHub scans

### Git commit

`feat(31): add scan status and detail retrieval endpoints`

---

## Prompt 32 — ZIP upload runs full extraction pipeline

### Objective

Connect `POST /api/v1/scans/upload` to the orchestrator; handle analysis failures without losing the scan_id.

### Why

Upload currently extracts then returns PENDING with no analysis. Prompt 31 may have hooked it; this commit finishes reliability (FAILED status, sanitized errors).

### Implementation

- On analysis exception: `status=failed`, persist `error_message` (sanitized), still return scan_id.
- Always cleanup extracted workspace.
- Do not execute archive contents.

### Files likely affected

- `backend/routers/scans.py`
- `tests/test_zip_ingestion.py`

### Verification

- Existing zip-slip tests still pass
- Happy-path ZIP scan details include ecosystems

### Completion criteria

- ZIP demo path: upload → completed/failed scan retrievable

### Git commit

`feat(32): run analysis pipeline on ZIP uploads`

---

## Prompt 33 — Controlled demo repository

### Objective

Add `demo-repository/` that always yields findings later (known ranges) without needing GitHub network during a talk.

### Why

Empty `demo-repository/` cannot be shown. External GitHub/OSV can fail.

### Implementation

- npm app: `package.json` with `lodash` range that OSV knows (e.g. `4.17.20`) plus a typosquat-like name for later heuristics (`lodahs` or similar **as a declared dep name only**).
- python: `requirements.txt` with an old `pyyaml` or `requests` pin suitable for OSV.
- Include a `package.json` `scripts.postinstall` string that must never run (for later static detection).
- Add `demo-repository/README.md` explaining it is synthetic.
- Optional: `scripts/pack-demo-zip.py` to zip the folder for upload.

### Files likely affected

- `demo-repository/**`
- `scripts/pack_demo_zip.py`

### Verification

- Orchestrator on demo folder lists expected packages
- Confirm no install scripts executed (patch subprocess)

### Completion criteria

- Demo tree is self-contained and parseable offline

### Git commit

`feat(33): add offline demo repository with known dependency fixtures`

---

## Prompt 34 — OSV HTTP vulnerability lookup with degradation

### Objective

Query OSV API for declared packages; if network fails, mark scanner `UNAVAILABLE` and complete the scan anyway.

### Why

No vulnerability logic exists. Demo needs CVEs without requiring syft/grype.

### Implementation

- `backend/scanners/osv.py`: POST `{osv_api_url}/querybatch` or per-package `/query` using `httpx`, timeout, no secrets in logs.
- Input: ecosystem + package name + version **spec**. If range is not a pinned version, query with the spec only when OSV accepts it; otherwise skip with `unresolved_range` note — do not invent a resolved version.
- Map vulns to `Finding` (`finding_type=vulnerability`, evidence = OSV IDs).
- Persist `scanner_status: { osv: SUCCESS|UNAVAILABLE|PARTIAL }`.
- Never call `osv-scanner` CLI in this commit (optional later).

### Files likely affected

- `backend/scanners/osv.py`
- `backend/pipeline/orchestrator.py`
- `tests/test_osv_scanner.py`

### Verification

- Mock httpx: finding created
- Mock timeout: scan still COMPLETED, osv UNAVAILABLE, zero invented CVEs

### Completion criteria

- Findings come only from OSV JSON; scan never crashes on OSV down

### Git commit

`feat(34): correlate declared dependencies with OSV vulnerabilities`

---

## Prompt 35 — Persist findings on scan detail

### Objective

Save findings via `ScanRepository.save_findings` and return them on `GET .../details`.

### Why

Repository already has findings persistence; API does not expose it.

### Implementation

- Orchestrator calls `save_findings`.
- Detail endpoint loads findings into `FindingResponse`.
- Include counts on the scan document.

### Files likely affected

- `backend/pipeline/orchestrator.py`
- `backend/routers/scans.py`
- `tests/test_scan_retrieval.py`

### Verification

- Mock OSV → details.findings non-empty
- Unknown scan 404

### Completion criteria

- Findings round-trip through repository + API

### Git commit

`feat(35): persist and return scan findings`

---

## Prompt 36 — Deterministic risk and priority

### Objective

Compute `RiskAssessment` from finding severities (0–100) and P0–P3 using existing `Severity.from_score` / `Priority.from_risk_score`.

### Why

Risk models exist but nothing calculates them. Demo needs a single score on the results page.

### Implementation

- `backend/risk/engine.py`: count CRITICAL/HIGH/MEDIUM/LOW; score from counts; blast_radius stub (e.g. direct vuln weight).
- Attach `remediation_advice` only from OSV `fixed_version` or “upgrade to a non-vulnerable version” — no LLM.
- Put `RiskResponse` on scan details.

### Files likely affected

- `backend/risk/engine.py`
- `backend/pipeline/orchestrator.py`
- `tests/test_risk_engine.py`

### Verification

- Zero findings → low/info score, P3
- One CRITICAL direct → high score, P0 or P1 per existing enum rules

### Completion criteria

- Details include overall_score and priority; formula is unit-tested

### Git commit

`feat(36): add deterministic scan risk scoring`

---

## Prompt 37 — Declared-dependency NetworkX graph

### Objective

Build a NetworkX DiGraph: repo root → each declared direct dependency. No lockfile/transitive resolution yet.

### Why

Graph schemas exist; no graph is built. Transitive graphs without lockfiles would be fake — do not fake them.

### Implementation

- `backend/graph/builder.py` using `networkx` (add to requirements).
- Nodes/edges match `GraphResponse` / Cytoscape fields.
- `has_cycles` false unless a later lockfile exists.
- Document limitation: direct declared deps only.

### Files likely affected

- `backend/graph/builder.py`
- `requirements.txt`
- `tests/test_graph_builder.py`

### Verification

- Demo package.json → node per declared dep, edges from root

### Completion criteria

- Graph generated without inventing transitive nodes

### Git commit

`feat(37): build declared-dependency graph with NetworkX`

---

## Prompt 38 — Graph on scan detail API

### Objective

Include `graph` in `ScanDetailResponse`.

### Why

Frontend Cytoscape payload must come from the backend.

### Implementation

- Orchestrator stores graph JSON on scan or rebuilds from dependencies on GET.
- Empty deps → empty nodes/edges, not null crash.

### Files likely affected

- `backend/routers/scans.py`
- `backend/pipeline/orchestrator.py`
- `tests/test_scan_retrieval.py`

### Verification

- GET details.graph.total_nodes matches dependency count + root

### Completion criteria

- API returns Cytoscape-compatible graph

### Git commit

`feat(38): expose dependency graph on scan detail API`

---

## Prompt 39 — Offline typosquatting heuristic

### Objective

Flag declared names within small edit distance of a bundled popular-package list (npm + pypi). No network.

### Why

Typosquatting is a demo-visible finding type already in enums.

### Implementation

- `backend/detectors/typosquat.py` + small `backend/detectors/popular_packages.json` (top names only).
- Skip if name is exactly in the popular list.
- FindingType.TYPOSQUATTING, evidence = compared name + distance.
- Never download packages.

### Files likely affected

- `backend/detectors/typosquat.py`
- `backend/detectors/popular_packages.json`
- `backend/pipeline/orchestrator.py`
- `tests/test_typosquat.py`

### Verification

- `lodahs` vs `lodash` flags; `lodash` does not

### Completion criteria

- Heuristic findings appear in details; no false “malware confirmed” language

### Git commit

`feat(39): detect likely typosquatted package names offline`

---

## Prompt 40 — Suspicious package.json lifecycle scripts

### Objective

Statically read `scripts` keys (`preinstall`, `postinstall`, `prepare`, `preuninstall`, etc.) and flag curl/wget/eval/node -e patterns as `SUSPICIOUS_LIFECYCLE_HOOK`.

### Why

Demo repo can include a hostile script string; security policy forbids executing it.

### Implementation

- JSON parse only.
- Evidence = script name + excerpt of command text.
- Do not run npm.

### Files likely affected

- `backend/detectors/lifecycle.py`
- `backend/parsers/package_json.py` (optional scripts metadata)
- `tests/test_lifecycle_detector.py`

### Verification

- `postinstall: curl ... | sh` → finding
- subprocess call count 0

### Completion criteria

- Lifecycle findings without executing scripts

### Git commit

`feat(40): flag suspicious npm lifecycle scripts statically`

---

## Prompt 41 — Minimal frontend shell and submit flow

### Objective

Create a vanilla HTML/JS frontend (no heavy framework unless already present — folder is empty) to submit GitHub URL or ZIP.

### Why

Cannot demo without a UI. Empty `frontend/`.

### Implementation

- `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`.
- Form: GitHub URL + optional branch; ZIP file input.
- POST to `http://127.0.0.1:8000/api/v1/scans/github` and `/api/v1/scans/upload`.
- CORS already allows `*` by default.
- After create, navigate/hash to scan id.
- Do not require Node build.

### Files likely affected

- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css`

### Verification

- Open `frontend/index.html` or serve `frontend` statically; submit mocked/local backend

### Completion criteria

- User can start a scan from the browser

### Git commit

`feat(41): add frontend scan submission page`

---

## Prompt 42 — Frontend status polling and results

### Objective

Poll `GET /api/v1/scans/{id}` then render details: risk, findings table, dependency list.

### Why

Submit without results is not a demo.

### Implementation

- Poll every 1–2s until completed/failed.
- Show scanner_status if present.
- Findings: severity, package, title, CVE/GHSA, remediation.
- Failed scans show error_message.

### Files likely affected

- `frontend/app.js`
- `frontend/index.html`
- `frontend/styles.css`

### Verification

- Manual: upload demo zip, see deps + findings

### Completion criteria

- Results view is usable for a live demo

### Git commit

`feat(42): poll scan status and render findings and risk`

---

## Prompt 43 — Frontend dependency graph view

### Objective

Render `details.graph` with Cytoscape.js from CDN (or simple SVG/list fallback if CDN blocked).

### Why

Graph API exists after 38; UI does not.

### Implementation

- New section “Dependency graph”.
- Fallback: nested list if Cytoscape fails to load.
- Do not require npm in frontend.

### Files likely affected

- `frontend/app.js`
- `frontend/index.html`

### Verification

- Demo scan shows root + declared packages

### Completion criteria

- Graph or readable fallback visible

### Git commit

`feat(43): visualize scan dependency graph in the frontend`

---

## Prompt 44 — Readable scan report

### Objective

`GET /api/v1/scans/{id}/report` returns Markdown (and JSON) assembled from persisted scan, findings, risk — no Grok required.

### Why

Demo needs a downloadable/readable report.

### Implementation

- `backend/reporting/markdown.py`
- Include scanner_status, limitations (direct deps only, no lockfile).
- Frontend “Download report” button.
- Optional Grok paragraph **only if** `GROK_API_KEY` set; must label “AI explanation, not a vuln database”. Skip if unset.

### Files likely affected

- `backend/reporting/markdown.py`
- `backend/routers/scans.py`
- `frontend/app.js`

### Verification

- Report contains score, finding titles, no invented CVEs

### Completion criteria

- Report endpoint + download works offline

### Git commit

`feat(44): generate markdown and JSON scan reports`

---

## Prompt 45 — Scanner status panel and graceful UI copy

### Objective

Surface `OSV: SUCCESS|UNAVAILABLE|...` (and Syft/Grype NOT_CONFIGURED) on health + results.

### Why

Demo must not look “broken” if OSV is down.

### Implementation

- Health already has binary flags; add scan-level `scanner_status`.
- Frontend banner: which analyzers ran.
- Do not implement Syft/Grype execution here.

### Files likely affected

- `backend/schemas/scan.py`
- `frontend/app.js`
- `frontend/index.html`

### Verification

- With OSV mocked down, UI shows UNAVAILABLE and still shows typosquat/lifecycle findings

### Completion criteria

- Partial scans are explained, not silent

### Git commit

`feat(45): show per-scanner status in API and UI`

---

## Prompt 46 — Critical-path integration test

### Objective

One pytest that zips `demo-repository`, POSTs upload, GETs details, asserts deps + at least one finding class (vuln **or** heuristic).

### Why

Need a single command proving the demo path.

### Implementation

- `tests/test_e2e_demo_zip.py` using TestClient.
- Mock OSV with a canned vuln so the test is offline-stable.
- Also assert subprocess npm not called.

### Files likely affected

- `tests/test_e2e_demo_zip.py`

### Verification

- `python -m pytest tests/test_e2e_demo_zip.py -q`

### Completion criteria

- E2E upload path passes without internet

### Git commit

`feat(46): add offline end-to-end ZIP scan integration test`

---

## Prompt 47 — Reliability and error-handling pass

### Objective

Fix crashes found while running e2e: missing 404s, CORS, empty files, huge JSON, Unicode BOM already handled, concurrent in-memory scans.

### Why

Demo failure modes.

### Implementation

- Review `error_handlers` leakage of paths.
- Ensure GET unknown scan_id is clean JSON.
- Cap findings list if needed.
- Keep security: no shell, no install.

### Files likely affected

- `backend/error_handlers.py`
- `backend/routers/scans.py`
- `tests/test_error_handling.py`

### Verification

- Re-run e2e + error-handling tests

### Completion criteria

- No unhandled 500 on bad scan_id / empty zip (already rejected)

### Git commit

`fix(47): harden scan API error paths for demo reliability`

---

## Prompt 48 — Setup documentation and demo script

### Objective

README that a teammate can follow in 10 minutes: venv, install, run backend, open frontend, upload demo zip.

### Why

`docs/` empty; README stops after `.env`.

### Implementation

- Fill README getting started, architecture (honest: what’s implemented vs not).
- `scripts/run_backend.ps1` / `.sh` optional.
- Document limitations: no lockfile/transitive, Syft/Grype unused, Firebase optional.

### Files likely affected

- `README.md`
- `docs/LIMITATIONS.md`
- `scripts/run_backend.ps1`

### Verification

- Follow README on a clean checklist (manual)

### Completion criteria

- Another person can start the demo from README

### Git commit

`docs(48): add demo setup instructions and limitations`

---

## Prompt 49 — Security review of untrusted input paths

### Objective

Re-read cloner, zip extractor, parsers, OSV client, frontend fetch URLs. Confirm no repo code execution and no secret logging.

### Why

Deadline pressure must not add `npm install` or `shell=True`.

### Implementation

- Add/adjust tests if a gap is found.
- Document residual risk in `docs/LIMITATIONS.md`.
- Do not “fix” by running packages.

### Files likely affected

- `tests/test_security_hardening.py`
- `docs/LIMITATIONS.md`

### Verification

- Existing security tests still pass
- New assertion: orchestrator does not call npm/pip

### Completion criteria

- Written security review notes; gaps tracked honestly

### Git commit

`chore(49): security review untrusted repository analysis paths`

---

## Prompt 50 — Final demo verification

### Objective

Run the real local demo once; record results in IMPLEMENTATION_PLAN. Fix only blockers.

### Why

Must not claim demo-ready without an actual pass.

### Implementation

- Start backend, open frontend, upload demo zip, record: ecosystems, dep count, findings, risk, graph, report.
- Update IMPLEMENTATION_PLAN Final Status (demo ready vs not).
- Do not add new detectors in this commit unless a blocker.

### Files likely affected

- `IMPLEMENTATION_PLAN.md`

### Verification

- Checklist in master prompt section 22

### Completion criteria

- Plan file matches observed behavior

### Git commit

`docs(50): record end-to-end demo verification results`
