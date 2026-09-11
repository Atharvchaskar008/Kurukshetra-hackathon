"""
SupplyGuard Repository Ingestion Package.

Provides secure ingestion, URL validation, safe repository cloning,
and workspace isolation against untrusted/hostile repositories.
"""

from backend.ingestion.git_cloner import GitCloner
from backend.ingestion.url_validator import ValidatedRepoURL, validate_github_url
from backend.ingestion.workspace import RepositoryWorkspace

__all__ = [
    "validate_github_url",
    "ValidatedRepoURL",
    "RepositoryWorkspace",
    "GitCloner",
]
