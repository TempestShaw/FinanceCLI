import zipfile
from pathlib import Path

from scripts.package_skills import build_skill_zip


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "finance-cli"


def test_finance_cli_skill_uses_public_cli_interface():
    skill_text = (SKILL_ROOT / "SKILL.md").read_text()

    assert "finance ... --output json" in skill_text
    assert "public interface" in skill_text
    assert "custom Python entrypoints" in skill_text
    assert not (SKILL_ROOT / "scripts").exists()
    assert "python scripts/" not in skill_text.lower()


def test_package_skills_zip_contains_only_instruction_docs(tmp_path):
    output_path = tmp_path / "finance-cli-skills.zip"

    result_path = build_skill_zip(output_path)

    assert result_path == output_path
    assert output_path.is_file()

    with zipfile.ZipFile(output_path) as archive:
        names = set(archive.namelist())

    assert "skills/finance-cli/SKILL.md" in names
    assert "skills/finance-cli/docs/ROUTING.md" in names
    assert "skills/finance-cli/docs/PLAYBOOKS.md" in names
    assert "skills/finance-cli/docs/TRUST.md" in names
    assert not any("/scripts/" in name for name in names)
    assert not any(name.endswith(".DS_Store") for name in names)
    assert not any("__pycache__" in name for name in names)
    assert not any("/build/" in name or "/dist/" in name for name in names)
    assert not any(name.startswith("skills/finance-cli/schemas/") for name in names)
