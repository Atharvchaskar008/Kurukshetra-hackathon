"""
Scan Ingestion Router for SupplyGuard.

Handles repository submission via GitHub URL and ZIP archive uploads.
Enforces size boundaries, sandboxing, and initiates scan documents.
"""

from __future__ import annotations

import logging
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from backend.config import get_settings
from backend.database.repository import get_scan_repository
from backend.exceptions import (
    DocumentNotFoundError,
    RepoSizeLimitExceededError,
    RepositoryIngestionError,
    ValidationError,
)
from backend.ingestion.git_cloner import GitCloner
from backend.ingestion.zip_extractor import ZipExtractor
from backend.models.domain import Repository, Scan
from backend.models.enums import ScanStatus
from backend.pipeline import run_scan
from backend.schemas.scan import (
    DependencyResponse,
    GitHubScanRequest,
    ScanCreateResponse,
    ScanDetailResponse,
    ScanStatusResponse,
)

logger = logging.getLogger("supplyguard.routers.scans")
router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("/upload", response_model=ScanCreateResponse, summary="Upload Repository ZIP Archive")
async def upload_zip_archive(file: UploadFile = File(...)) -> ScanCreateResponse:
    """
    Accept and securely ingest a repository source archive in ZIP format.

    - Enforces max upload size limits
    - Defends against Zip Slip and directory traversal
    - Sandboxes extraction into an isolated workspace
    - Never executes extracted content
    - Returns unique scan_id tracking token
    """
    settings = get_settings()

    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise ValidationError("Only .zip repository archives are supported.")

    scan_id = str(uuid.uuid4())
    logger.info("Received ZIP archive upload '%s' for scan_id=%s", file.filename, scan_id)

    # Stream upload to temporary file while enforcing max_upload_size_bytes
    temp_zip = Path(tempfile.gettempdir()) / f"upload_{scan_id}.zip"
    uploaded_bytes = 0
    workspace = None

    try:
        with open(temp_zip, "wb") as buffer:
            while True:
                chunk = await file.read(64 * 1024)
                if not chunk:
                    break
                uploaded_bytes += len(chunk)
                if uploaded_bytes > settings.max_upload_size_bytes:
                    raise RepoSizeLimitExceededError(
                        f"Uploaded ZIP size ({uploaded_bytes} bytes) exceeds limit of {settings.max_upload_size_bytes} bytes."
                    )
                buffer.write(chunk)

        if uploaded_bytes == 0:
            raise ValidationError("Uploaded ZIP archive is empty.")

        # Extract and validate securely via ZipExtractor into sandboxed workspace
        extractor = ZipExtractor(
            max_files=settings.max_scan_files,
            max_extracted_size_bytes=settings.max_extracted_size_bytes,
            max_single_file_size_bytes=settings.max_single_file_size_bytes,
            timeout_seconds=settings.zip_extraction_timeout_seconds,
        )
        workspace = extractor.extract(temp_zip)

        # Inspect extracted workspace metadata
        files = workspace.list_files()
        file_count = len(files)

        repo_metadata = Repository(
            url=f"upload:{file.filename}",
            name=Path(file.filename).stem,
            file_count=file_count,
            size_bytes=uploaded_bytes,
            metadata={"source": "zip_upload", "original_filename": file.filename},
        )

        scan_doc = Scan(
            scan_id=scan_id,
            repository=repo_metadata,
            status=ScanStatus.PENDING,
        )

        # Persist initial scan document
        repo = get_scan_repository()
        repo.create_scan(scan_id, scan_doc)

        logger.info(
            "ZIP archive '%s' successfully ingested into workspace (%d files). Scan ID: %s",
            file.filename,
            file_count,
            scan_id,
        )

        result = run_scan(scan_id, workspace, repo_metadata)
        status = ScanStatus(result.get("status", ScanStatus.COMPLETED.value))
        return ScanCreateResponse(
            scan_id=scan_id,
            status=status,
            target=f"upload:{file.filename}",
            message="Repository ZIP archive uploaded and analyzed.",
        )

    finally:
        try:
            if workspace is not None:
                workspace.cleanup()
        except Exception:
            pass
        if temp_zip.exists():
            try:
                temp_zip.unlink()
            except Exception:
                pass


@router.post("", response_model=ScanCreateResponse, summary="Initiate repository security scan")
@router.post("/github", response_model=ScanCreateResponse, summary="Scan GitHub repository")
async def create_github_scan(payload: GitHubScanRequest) -> ScanCreateResponse:
    target_url = payload.get_url()
    scan_id = str(uuid.uuid4())
    cloner = GitCloner()
    workspace = None
    try:
        workspace = cloner.clone(
            target_url,
            branch=payload.branch,
            commit_hash=payload.commit_hash,
        )
        files = workspace.list_files()
        repo_metadata = Repository(
            url=target_url,
            name=target_url.rstrip("/").split("/")[-1],
            default_branch=payload.branch or "main",
            commit_hash=payload.commit_hash,
            file_count=len(files),
            metadata={"source": "github"},
        )
        store = get_scan_repository()
        store.create_scan(scan_id, Scan(scan_id=scan_id, repository=repo_metadata, status=ScanStatus.PENDING))
        result = run_scan(scan_id, workspace, repo_metadata)
        status = ScanStatus(result.get("status", ScanStatus.COMPLETED.value))
        return ScanCreateResponse(
            scan_id=scan_id,
            status=status,
            target=target_url,
            message="GitHub repository cloned and analyzed.",
        )
    finally:
        if workspace is not None:
            try:
                workspace.cleanup()
            except Exception:
                pass


def _load_scan(scan_id: str) -> dict:
    doc = get_scan_repository().get_scan(scan_id)
    if not doc:
        raise DocumentNotFoundError(f"Scan {scan_id} was not found.")
    return doc


@router.get("/{scan_id}", response_model=ScanStatusResponse, summary="Get scan status")
async def get_scan_status(scan_id: str) -> ScanStatusResponse:
    doc = _load_scan(scan_id)
    return ScanStatusResponse(
        scan_id=scan_id,
        status=doc.get("status", ScanStatus.PENDING),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
        completed_at=doc.get("completed_at"),
        progress_percent=float(doc.get("progress_percent") or 0.0),
        current_stage=doc.get("current_stage", "queued"),
        error_message=doc.get("error_message"),
    )


@router.get("/{scan_id}/details", response_model=ScanDetailResponse, summary="Get scan details")
async def get_scan_details(scan_id: str) -> ScanDetailResponse:
    doc = _load_scan(scan_id)
    raw_deps = doc.get("dependencies") or []
    dependencies = [DependencyResponse.model_validate(item) for item in raw_deps]
    return ScanDetailResponse(
        scan_id=scan_id,
        status=doc.get("status", ScanStatus.PENDING),
        repository=doc.get("repository") or {},
        risk=doc.get("risk"),
        findings=[],
        dependencies=dependencies,
        graph=doc.get("graph"),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
        completed_at=doc.get("completed_at"),
    )
