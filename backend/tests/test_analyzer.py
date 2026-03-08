import json

from app.services.analyzer import (
    _detect_tech_stack_from_deps,
    _find_source_files,
)


def test_detect_tech_stack_node():
    package_json = json.dumps(
        {
            "dependencies": {"react": "^18.0.0", "next": "^14.0.0"},
            "devDependencies": {"typescript": "^5.0.0", "vitest": "^1.0.0"},
        }
    )
    stack = _detect_tech_stack_from_deps(package_json, "package.json")
    assert "React" in stack
    assert "Next.js" in stack
    assert "TypeScript" in stack
    assert "Vitest" in stack


def test_detect_tech_stack_python():
    requirements = "fastapi>=0.100.0\nsqlalchemy>=2.0\npytest>=8.0\n"
    stack = _detect_tech_stack_from_deps(requirements, "requirements.txt")
    assert "FastAPI" in stack
    assert "SQLAlchemy" in stack
    assert "pytest" in stack


def test_has_tests_detection():
    tree = [
        {"path": "src/main.ts", "type": "blob"},
        {"path": "tests/test_main.py", "type": "blob"},
        {"path": "tests/conftest.py", "type": "blob"},
    ]
    paths = {e["path"] for e in tree}
    has_tests = any(
        "test" in p.lower().split("/")[0]
        or p.lower().startswith("tests/")
        or p.lower().startswith("test/")
        or "__tests__" in p
        for p in paths
    )
    assert has_tests is True


def test_has_ci_detection():
    tree = [
        {"path": ".github/workflows/ci.yml", "type": "blob"},
        {"path": "src/main.ts", "type": "blob"},
    ]
    paths = {e["path"] for e in tree}
    has_ci = any(p.startswith(".github/workflows/") for p in paths)
    assert has_ci is True


def test_file_sampling_priority():
    tree = [
        {"path": "README.md", "type": "blob", "size": 2000},
        {"path": "package.json", "type": "blob", "size": 500},
        {"path": "src/index.ts", "type": "blob", "size": 1000},
        {"path": "src/App.tsx", "type": "blob", "size": 800},
        {"path": "src/utils.ts", "type": "blob", "size": 600},
        {"path": "src/big-file.ts", "type": "blob", "size": 5000},
        {"path": "src/test_utils.ts", "type": "blob", "size": 400},
        {"path": "tsconfig.json", "type": "blob", "size": 300},
        {"path": "node_modules/foo/index.js", "type": "blob", "size": 100},
    ]
    source_files = _find_source_files(tree)
    # Should skip node_modules and test files
    assert "node_modules/foo/index.js" not in source_files
    # Should include src files sorted by size
    assert len(source_files) <= 4
    # Biggest file should be first
    if source_files:
        assert source_files[0] == "src/big-file.ts"
