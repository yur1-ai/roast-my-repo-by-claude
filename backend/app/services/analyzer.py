import json
import logging
import os

from app.schemas.roast import RepoMetadata
from app.services import github

logger = logging.getLogger(__name__)

# Config file indicators for tech stack detection
_PACKAGE_MANIFESTS = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
    "pom.xml",
    "build.gradle",
}

_CONFIG_FILES = {
    "tsconfig.json",
    ".eslintrc.json",
    ".eslintrc.js",
    ".eslintrc.yml",
    "Dockerfile",
    "docker-compose.yml",
    ".prettierrc",
    "vite.config.ts",
    "vite.config.js",
    "next.config.js",
    "next.config.mjs",
    "webpack.config.js",
}

_SKIP_DIRS = {"node_modules", "dist", "build", ".git", "vendor", "__pycache__", ".next", "target"}
_SKIP_EXTENSIONS = {".min.js", ".min.css", ".lock", ".map", ".svg", ".png", ".jpg", ".ico", ".woff", ".woff2", ".ttf"}

_ENTRY_POINTS = [
    "src/index.ts", "src/index.tsx", "src/main.ts", "src/main.tsx",
    "src/index.js", "src/index.jsx", "src/main.js", "src/main.jsx",
    "src/App.tsx", "src/App.ts", "src/app.ts",
    "main.py", "app.py", "app/main.py", "src/main.py",
    "src/lib.rs", "src/main.rs",
    "main.go", "cmd/main.go",
    "index.ts", "index.js",
]


def _should_skip_path(path: str) -> bool:
    parts = path.split("/")
    for part in parts:
        if part in _SKIP_DIRS:
            return True
    _, ext = os.path.splitext(path)
    return ext in _SKIP_EXTENSIONS


def _detect_tech_stack_from_deps(content: str, filename: str) -> list[str]:
    stack = []

    if filename == "package.json":
        try:
            data = json.loads(content)
            all_deps = {}
            all_deps.update(data.get("dependencies", {}))
            all_deps.update(data.get("devDependencies", {}))

            dep_map = {
                "react": "React",
                "next": "Next.js",
                "vue": "Vue",
                "angular": "Angular",
                "@angular/core": "Angular",
                "express": "Express",
                "fastify": "Fastify",
                "svelte": "Svelte",
                "typescript": "TypeScript",
                "tailwindcss": "Tailwind CSS",
                "vite": "Vite",
                "webpack": "webpack",
                "jest": "Jest",
                "vitest": "Vitest",
                "mocha": "Mocha",
                "prisma": "Prisma",
                "drizzle-orm": "Drizzle",
            }

            for dep, name in dep_map.items():
                if dep in all_deps:
                    stack.append(name)
        except json.JSONDecodeError:
            pass

    elif filename in ("requirements.txt", "pyproject.toml"):
        content_lower = content.lower()
        dep_map = {
            "django": "Django",
            "flask": "Flask",
            "fastapi": "FastAPI",
            "sqlalchemy": "SQLAlchemy",
            "celery": "Celery",
            "pytest": "pytest",
            "numpy": "NumPy",
            "pandas": "Pandas",
            "tensorflow": "TensorFlow",
            "torch": "PyTorch",
        }
        for dep, name in dep_map.items():
            if dep in content_lower:
                stack.append(name)

    elif filename == "Cargo.toml":
        dep_map = {
            "actix": "Actix",
            "tokio": "Tokio",
            "rocket": "Rocket",
            "serde": "Serde",
        }
        content_lower = content.lower()
        for dep, name in dep_map.items():
            if dep in content_lower:
                stack.append(name)

    elif filename == "go.mod":
        dep_map = {
            "gin-gonic": "Gin",
            "echo": "Echo",
            "fiber": "Fiber",
        }
        content_lower = content.lower()
        for dep, name in dep_map.items():
            if dep in content_lower:
                stack.append(name)

    return stack


def _detect_language_from_extensions(tree: list[dict]) -> dict[str, int]:
    ext_counts: dict[str, int] = {}
    ext_to_lang = {
        ".ts": "TypeScript", ".tsx": "TypeScript",
        ".js": "JavaScript", ".jsx": "JavaScript",
        ".py": "Python",
        ".rs": "Rust",
        ".go": "Go",
        ".java": "Java",
        ".rb": "Ruby",
        ".php": "PHP",
        ".cs": "C#",
        ".cpp": "C++", ".cc": "C++", ".cxx": "C++",
        ".c": "C",
        ".swift": "Swift",
        ".kt": "Kotlin",
    }

    for entry in tree:
        if entry.get("type") != "blob":
            continue
        path = entry.get("path", "")
        if _should_skip_path(path):
            continue
        _, ext = os.path.splitext(path)
        if ext in ext_to_lang:
            lang = ext_to_lang[ext]
            ext_counts[lang] = ext_counts.get(lang, 0) + 1

    return ext_counts


def _find_source_files(tree: list[dict]) -> list[str]:
    """Find source files from the most populated source directory."""
    source_dirs = {}
    source_exts = {".ts", ".tsx", ".js", ".jsx", ".py", ".rs", ".go", ".java", ".rb"}

    for entry in tree:
        if entry.get("type") != "blob":
            continue
        path = entry.get("path", "")
        if _should_skip_path(path):
            continue
        _, ext = os.path.splitext(path)
        if ext not in source_exts:
            continue

        # Get top-level directory
        parts = path.split("/")
        if len(parts) > 1:
            top_dir = parts[0]
            if top_dir not in source_dirs:
                source_dirs[top_dir] = []
            source_dirs[top_dir].append(entry)

    if not source_dirs:
        return []

    # Pick the most populated directory (typically src/, lib/, app/)
    preferred = ["src", "lib", "app", "pkg", "internal"]
    best_dir = None
    for d in preferred:
        if d in source_dirs:
            best_dir = d
            break
    if not best_dir:
        best_dir = max(source_dirs, key=lambda d: len(source_dirs[d]))

    # Sort by size descending, pick up to 4
    files = source_dirs[best_dir]
    files.sort(key=lambda e: e.get("size", 0), reverse=True)

    # Skip test files
    result = []
    for f in files:
        path = f["path"]
        basename = os.path.basename(path).lower()
        if basename.startswith("test_") or basename.endswith("_test.py") or ".test." in basename or ".spec." in basename:
            continue
        result.append(path)
        if len(result) >= 4:
            break

    return result


async def analyze_repo(owner: str, name: str, metadata: RepoMetadata) -> dict:
    tree = await github.fetch_repo_tree(owner, name, metadata.default_branch)

    # Count files (blobs only)
    file_count = sum(1 for e in tree if e.get("type") == "blob")

    # Detect languages from file extensions
    lang_counts = _detect_language_from_extensions(tree)

    # Check for key files/dirs
    paths = {e.get("path", "") for e in tree}
    has_readme = any(p.lower() == "readme.md" for p in paths)
    has_license = any(p.lower() in ("license", "license.md", "license.txt") for p in paths)
    has_contributing = any(p.lower() in ("contributing.md", "contributing") for p in paths)
    has_tests = any(
        "test" in p.lower().split("/")[0] or p.lower().startswith("tests/") or p.lower().startswith("test/") or "__tests__" in p
        for p in paths
    )
    has_ci = any(p.startswith(".github/workflows/") for p in paths)

    # Detect test framework
    test_framework = None
    if any("jest.config" in p for p in paths):
        test_framework = "jest"
    elif any("vitest" in p.lower() for p in paths):
        test_framework = "vitest"
    elif any("pytest" in p.lower() or "conftest.py" in p for p in paths):
        test_framework = "pytest"

    # Detect CI platform
    ci_platform = None
    if has_ci:
        ci_platform = "github_actions"
    elif any(".gitlab-ci" in p for p in paths):
        ci_platform = "gitlab_ci"
    elif any(".circleci" in p for p in paths):
        ci_platform = "circleci"

    # Build file sampling list
    files_to_sample: list[str] = []

    # 1. README
    if has_readme:
        files_to_sample.append("README.md")

    # 2. Entry points
    for entry in _ENTRY_POINTS:
        if entry in paths and entry not in files_to_sample:
            files_to_sample.append(entry)
            break

    # 3. Package manifests
    for manifest in _PACKAGE_MANIFESTS:
        if manifest in paths and manifest not in files_to_sample:
            files_to_sample.append(manifest)
            break

    # 4. Config files
    for config in _CONFIG_FILES:
        if config in paths and config not in files_to_sample:
            files_to_sample.append(config)
            break

    # 5. Source files from main directory (up to 4)
    source_files = _find_source_files(tree)
    for sf in source_files:
        if sf not in files_to_sample and len(files_to_sample) < 8:
            files_to_sample.append(sf)

    # Fetch file contents
    tech_stack: list[str] = list(lang_counts.keys())
    sampled_files: list[dict] = []
    findings: list[dict] = []

    for file_path in files_to_sample:
        content = await github.fetch_file_content(owner, name, file_path)
        if content is None:
            continue

        lines = content.split("\n")
        preview = "\n".join(lines[:200])

        sampled_files.append({
            "path": file_path,
            "lines": len(lines),
            "preview": preview,
        })

        # Detect tech stack from package manifests
        basename = os.path.basename(file_path)
        if basename in _PACKAGE_MANIFESTS:
            detected = _detect_tech_stack_from_deps(content, basename)
            for item in detected:
                if item not in tech_stack:
                    tech_stack.append(item)

    return {
        "tech_stack": tech_stack,
        "file_count": file_count,
        "has_tests": has_tests,
        "has_ci": has_ci,
        "has_readme": has_readme,
        "has_license": has_license,
        "has_contributing": has_contributing,
        "test_framework": test_framework,
        "ci_platform": ci_platform,
        "findings": findings,
        "sampled_files": sampled_files,
    }
