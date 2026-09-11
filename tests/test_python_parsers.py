from pathlib import Path
from unittest.mock import patch

from backend.ingestion import RepositoryWorkspace
from backend.models.enums import Ecosystem
from backend.parsers import parse_pyproject_toml, parse_requirements_txt
from backend.pipeline import run_scan
from backend.database.repository import get_scan_repository, reset_repository_for_testing


def test_requirements_txt_preserves_specifiers():
    text = Path("tests/fixtures/ecosystems/python_project/requirements.txt").read_text(encoding="utf-8")
    deps = {d.package_name: d for d in parse_requirements_txt(text)}
    assert deps["requests"].version == ">=2.31.0"
    assert deps["fastapi"].version == "==0.110.0"
    assert deps["fastapi"].is_pinned is True
    assert deps["uvicorn"].version == ">=0.28.0"
    assert deps["uvicorn"].ecosystem == Ecosystem.PYPI
    assert deps["uvicorn"].metadata.get("extras") == "standard"


def test_requirements_skips_includes_and_comments():
    text = "# comment\n-r other.txt\n-e git+https://example.com/x.git#egg=x\nflask==3.0.0  # pin\n"
    deps = parse_requirements_txt(text)
    assert [d.package_name for d in deps] == ["flask"]
    assert deps[0].version == "==3.0.0"


def test_pyproject_project_dependencies():
    text = Path("tests/fixtures/ecosystems/python_project/pyproject.toml").read_text(encoding="utf-8")
    deps = parse_pyproject_toml(text)
    assert len(deps) == 1
    assert deps[0].package_name == "pydantic"
    assert deps[0].version == ">=2.6.0"


def test_orchestrator_extracts_npm_and_python(tmp_path):
    reset_repository_for_testing()
    (tmp_path / "package.json").write_text(
        '{"name":"app","version":"1.0.0","dependencies":{"express":"^4.18.2"}}',
        encoding="utf-8",
    )
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n", encoding="utf-8")
    store = get_scan_repository()
    store.create_scan("s1", {"scan_id": "s1", "status": "pending"})
    with RepositoryWorkspace(workspace_dir=tmp_path, auto_cleanup=False) as ws:
        with patch("subprocess.run") as mock_run:
            result = run_scan("s1", ws)
            assert mock_run.call_count == 0
    assert result["status"] == "completed"
    names = {d["package_name"] for d in result["dependencies"]}
    assert names == {"express", "requests"}
    assert "^4.18.2" in {d["version"] for d in result["dependencies"]}
    assert "==2.31.0" in {d["version"] for d in result["dependencies"]}
