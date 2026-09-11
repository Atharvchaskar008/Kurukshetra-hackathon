/**
 * SupplyGuard Dashboard — Application Logic
 *
 * Handles scan submission, polling, and results rendering.
 * Communicates with /api/v1/scans endpoints.
 */

const API_BASE = window.location.origin + "/api/v1";

// DOM refs
const repoInput = document.getElementById("repo-url");
const analyzeBtn = document.getElementById("analyze-btn");
const scanStatus = document.getElementById("scan-status");
const resultsPanel = document.getElementById("results-panel");
const scoreValue = document.getElementById("score-value");
const scoreRingFill = document.getElementById("score-ring-fill");
const riskBadge = document.getElementById("risk-badge");
const ecosystemsBar = document.getElementById("ecosystems-bar");
const findingsTbody = document.getElementById("findings-tbody");
const noFindings = document.getElementById("no-findings");
const depsList = document.getElementById("deps-list");

// Summary card values
const valDeps = document.getElementById("val-deps");
const valFindings = document.getElementById("val-findings");
const valCritical = document.getElementById("val-critical");
const valHigh = document.getElementById("val-high");
const valMedium = document.getElementById("val-medium");
const valLow = document.getElementById("val-low");

// Allow Enter key
repoInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") startScan();
});

async function startScan() {
    const url = repoInput.value.trim();
    if (!url) {
        showStatus("Please enter a repository URL.", "error");
        return;
    }

    analyzeBtn.disabled = true;
    resultsPanel.classList.add("hidden");
    showStatus("⏳ Submitting scan request...", "loading");

    try {
        const res = await fetch(`${API_BASE}/scans`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ repo_url: url }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const createData = await res.json();
        const scanId = createData.scan_id;

        // Fetch complete scan results (score, risk_level, findings, dependencies)
        showStatus("⏳ Analyzing repository security signals...", "loading");
        const resultsRes = await fetch(`${API_BASE}/scans/${scanId}/results`);
        if (!resultsRes.ok) {
            const err = await resultsRes.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${resultsRes.status}`);
        }

        const data = await resultsRes.json();
        showStatus("✅ Scan completed! Rendering results...", "success");
        renderResults(data);

    } catch (err) {
        showStatus(`❌ Scan failed: ${err.message}`, "error");
    } finally {
        analyzeBtn.disabled = false;
    }
}

function showStatus(msg, type) {
    scanStatus.textContent = msg;
    scanStatus.className = `scan-status ${type}`;
    scanStatus.classList.remove("hidden");
}

function renderResults(data) {
    resultsPanel.classList.remove("hidden");

    // Score ring
    const score = data.score ?? 100;
    const circumference = 2 * Math.PI * 52; // r=52
    const offset = circumference - (score / 100) * circumference;
    scoreRingFill.style.strokeDashoffset = offset;
    animateCounter(scoreValue, score);

    // Risk badge
    const risk = data.risk_level || "SAFE";
    riskBadge.textContent = risk;
    riskBadge.className = `risk-badge risk-${risk}`;

    // Summary cards
    const deps = data.dependencies || [];
    const findings = data.findings || [];

    valDeps.textContent = data.dependency_count || deps.length;
    valFindings.textContent = findings.length;

    let critCount = 0, highCount = 0, medCount = 0, lowCount = 0;
    findings.forEach(f => {
        const s = (f.severity || "").toUpperCase();
        if (s === "CRITICAL") critCount++;
        else if (s === "HIGH") highCount++;
        else if (s === "MEDIUM") medCount++;
        else lowCount++;
    });
    valCritical.textContent = critCount;
    valHigh.textContent = highCount;
    valMedium.textContent = medCount;
    valLow.textContent = lowCount;

    // Ecosystems
    ecosystemsBar.innerHTML = "";
    const ecos = data.ecosystems || [];
    ecos.forEach((eco) => {
        const tag = document.createElement("span");
        tag.className = "eco-tag";
        tag.textContent = eco;
        ecosystemsBar.appendChild(tag);
    });

    // Findings table
    findingsTbody.innerHTML = "";

    if (findings.length === 0) {
        noFindings.classList.remove("hidden");
        document.querySelector(".findings-table").classList.add("hidden");
    } else {
        noFindings.classList.add("hidden");
        document.querySelector(".findings-table").classList.remove("hidden");

        findings.forEach((f) => {
            const tr = document.createElement("tr");
            const priority = f.priority || "P3";
            const sev = (f.severity || "UNKNOWN").toUpperCase();
            const confidence = f.confidence != null ? `${(f.confidence * 100).toFixed(0)}%` : "—";
            const blast = f.blast_radius != null ? f.blast_radius.toFixed(2) : "—";
            const detailText = f.title || f.summary || f.type || "";

            tr.innerHTML = `
                <td><span class="priority-${priority}">${priority}</span></td>
                <td><strong>${escapeHtml(f.package || "—")}</strong></td>
                <td>${escapeHtml(f.type || "—")}</td>
                <td><span class="sev-badge sev-${sev}">${sev}</span></td>
                <td>${confidence}</td>
                <td>${blast}</td>
                <td class="finding-detail">${escapeHtml(detailText)}</td>
            `;
            findingsTbody.appendChild(tr);
        });
    }

    // Dependencies list
    depsList.innerHTML = "";
    const deps = data.dependencies || [];
    deps.forEach((d) => {
        const chip = document.createElement("span");
        chip.className = "dep-chip";
        const name = d.package || d.package_name || "unknown";
        const version = d.version || "*";
        chip.innerHTML = `${escapeHtml(name)}<span class="dep-version">@${escapeHtml(version)}</span>`;
        depsList.appendChild(chip);
    });

    // Smooth scroll to results
    resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function animateCounter(el, target) {
    const duration = 1000;
    const start = performance.now();
    const startVal = 0;

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = startVal + (target - startVal) * eased;
        el.textContent = current.toFixed(1);
        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
