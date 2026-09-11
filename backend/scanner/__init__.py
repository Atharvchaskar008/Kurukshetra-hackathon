"""
Security Scanners & Vulnerability Analysis for Depscan.
"""

from backend.scanner.osv import OSVScanner, query_osv_vulnerabilities

__all__ = ["OSVScanner", "query_osv_vulnerabilities"]
