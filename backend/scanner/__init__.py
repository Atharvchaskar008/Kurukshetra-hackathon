"""
Security Scanners & Vulnerability Analysis for Depscan.
"""

from backend.scanner.heuristics import (
    SupplyChainHeuristicsScanner,
    detect_dependency_confusion,
    detect_typosquatting,
)
from backend.scanner.osv import OSVScanner, query_osv_vulnerabilities

__all__ = [
    "OSVScanner",
    "query_osv_vulnerabilities",
    "SupplyChainHeuristicsScanner",
    "detect_typosquatting",
    "detect_dependency_confusion",
]
