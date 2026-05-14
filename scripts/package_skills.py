"""Package Finance CLI agent skills for the docs site."""
from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_SOURCE = ROOT / "skills" / "finance-cli"
DEFAULT_OUTPUT = ROOT / "docs-site" / "public" / "skills" / "finance-cli-skills.zip"
ZIP_ROOT = Path("skills") / "finance-cli"
ALLOWED_ROOT_FILES = {"SKILL.md"}
ALLOWED_DOC_SUFFIXES = {".md"}
BLOCKED_NAMES = {
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
}
BLOCKED_PARTS = {"scripts", "schemas", "build", "dist", "node_modules", ".astro"}


def build_skill_zip(output_path: Path = DEFAULT_OUTPUT, skill_source: Path = SKILL_SOURCE) -> Path:
    """Build the downloadable skill zip."""
    skill_source = skill_source.resolve()
    output_path = output_path.resolve()
    _validate_skill_source(skill_source)

    files = _skill_files(skill_source)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(skill_source)
            archive.write(path, (ZIP_ROOT / relative).as_posix())
    return output_path


def _validate_skill_source(skill_source: Path) -> None:
    if not skill_source.is_dir():
        raise FileNotFoundError(f"Skill source not found: {skill_source}")
    if not (skill_source / "SKILL.md").is_file():
        raise FileNotFoundError(f"Missing skill entrypoint: {skill_source / 'SKILL.md'}")
    if (skill_source / "scripts").exists():
        raise ValueError("Unexpected executable resources in skill package: scripts/")


def _skill_files(skill_source: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(skill_source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(skill_source)
        if _blocked(relative):
            raise ValueError(f"Blocked file in skill package: {relative}")
        if _allowed(relative):
            files.append(path)
            continue
        raise ValueError(f"Unexpected file in skill package: {relative}")
    return files


def _allowed(relative: Path) -> bool:
    if len(relative.parts) == 1:
        return relative.name in ALLOWED_ROOT_FILES
    return relative.parts[0] == "docs" and relative.suffix in ALLOWED_DOC_SUFFIXES


def _blocked(relative: Path) -> bool:
    return any(part in BLOCKED_NAMES or part in BLOCKED_PARTS for part in relative.parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Finance CLI skill zip.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination zip path.",
    )
    args = parser.parse_args()

    output_path = build_skill_zip(args.output)
    try:
        display_path = output_path.relative_to(ROOT)
    except ValueError:
        display_path = output_path
    print(os.fspath(display_path))


if __name__ == "__main__":
    main()
