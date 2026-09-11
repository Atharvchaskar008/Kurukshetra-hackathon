"""Scan pipeline: ecosystems + declared dependencies. No package installs."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from backend.database.repository import get_scan_repository
from backend.ecosystems import detect_ecosystems
from backend.ecosystems.models import ManifestType
from backend.ingestion.workspace import RepositoryWorkspace
from backend.models.domain import Repository
from backend.models.enums import ScanStatus
from backend.parsers.package_json import parse_package_json_file
from backend.parsers.python_deps import parse_pyproject_toml_file, parse_requirements_txt_file

logger = logging.getLogger("supplyguard.pipeline")


def run_scan(
    scan_id: str,
    workspace: RepositoryWorkspace,
    repository: Repository | None = None,
) -> Dict[str, Any]:
    store = get_scan_repository()
    store.update_scan(
        scan_id,
        {"status": ScanStatus.SCANNING.value, "current_stage": "ecosystems", "progress_percent": 20},
    )
    try:
        detection = detect_ecosystems(workspace)
        store.update_scan(scan_id, {"current_stage": "dependencies", "progress_percent": 50})

        declared: List[Dict[str, Any]] = []
        root = workspace.root_path
        for manifest in detection.manifest_inventory:
            full = root / manifest.path
            if manifest.manifest_type == ManifestType.PACKAGE_JSON:
                parsed = parse_package_json_file(full, source_path=manifest.path)
                declared.extend(d.to_dependency().model_dump(mode="json") for d in parsed.dependencies)
            elif manifest.manifest_type == ManifestType.REQUIREMENTS_TXT:
                declared.extend(
                    d.to_dependency().model_dump(mode="json")
                    for d in parse_requirements_txt_file(full, source_path=manifest.path)
                )
            elif manifest.manifest_type == ManifestType.PYPROJECT_TOML:
                declared.extend(
                    d.to_dependency().model_dump(mode="json")
                    for d in parse_pyproject_toml_file(full, source_path=manifest.path)
                )

        from datetime import datetime, timezone

        payload: Dict[str, Any] = {
            "status": ScanStatus.COMPLETED.value,
            "current_stage": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "progress_percent": 100.0,
            "dependencies": declared,
            "dependencies_count": len(declared),
            "direct_dependencies_count": len(declared),
            "transitive_dependencies_count": 0,
            "findings_count": 0,
            "ecosystems_detected": [e.value for e in detection.ecosystems],
            "is_monorepo": detection.is_monorepo,
            "is_multilanguage": detection.is_multilanguage,
            "scanner_status": {"osv": "NOT_RUN", "syft": "NOT_CONFIGURED", "grype": "NOT_CONFIGURED"},
        }
        if repository is not None:
            payload["repository"] = repository.model_dump(mode="json")
            payload["repository"]["ecosystems_detected"] = payload["ecosystems_detected"]
        updated = store.update_scan(scan_id, payload)
        return updated or payload
    except Exception as exc:
        logger.exception("Scan %s failed", scan_id)
        failed = store.update_scan(
            scan_id,
            {
                "status": ScanStatus.FAILED.value,
                "current_stage": "failed",
                "error_message": str(exc)[:500],
                "progress_percent": 100.0,
            },
        )
        return failed or {}
