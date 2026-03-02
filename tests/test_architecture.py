import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _iter_python_files(relative_dir: str) -> list[Path]:
    base = PROJECT_ROOT / relative_dir
    return [p for p in base.rglob("*.py") if p.is_file()]


def _imports_in_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def test_domain_has_no_framework_or_outer_layer_dependencies() -> None:
    forbidden_prefixes = (
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "uvicorn",
        "app.application",
        "app.infrastructure",
    )

    violations: list[str] = []
    for py_file in _iter_python_files("app/domain"):
        for imported in _imports_in_file(py_file):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{py_file}: {imported}")

    assert not violations, "\n".join(violations)


def test_application_does_not_import_infrastructure_or_web_frameworks() -> None:
    forbidden_prefixes = (
        "fastapi",
        "sqlalchemy",
        "app.infrastructure",
    )

    violations: list[str] = []
    for py_file in _iter_python_files("app/application"):
        for imported in _imports_in_file(py_file):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{py_file}: {imported}")

    assert not violations, "\n".join(violations)
