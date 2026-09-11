"""
Static manifest parsers for Depscan / SupplyGuard.

All parsers operate on inert text/JSON. They never invoke package managers
or execute lifecycle scripts from untrusted repositories.
"""

from backend.parsers.models import (
    DeclaredDependency,
    NestedPackageJsonParseResult,
    NpmDependencySection,
    PackageJsonParseResult,
    PackageManagerMetadata,
    WorkspaceParseResult,
)
from backend.parsers.package_json import (
    parse_nested_package_jsons,
    parse_package_json,
    parse_package_json_file,
    parse_workspace_package_jsons,
)
from backend.parsers.python_deps import (
    parse_pyproject_toml,
    parse_pyproject_toml_file,
    parse_requirements_txt,
    parse_requirements_txt_file,
)

__all__ = [
    "DeclaredDependency",
    "NestedPackageJsonParseResult",
    "NpmDependencySection",
    "PackageJsonParseResult",
    "PackageManagerMetadata",
    "WorkspaceParseResult",
    "parse_nested_package_jsons",
    "parse_package_json",
    "parse_package_json_file",
    "parse_workspace_package_jsons",
    "parse_pyproject_toml",
    "parse_pyproject_toml_file",
    "parse_requirements_txt",
    "parse_requirements_txt_file",
]
