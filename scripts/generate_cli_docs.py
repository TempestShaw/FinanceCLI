"""Generate Markdown command reference from the Finance CLI registry."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.registry import clear_commands, list_commands


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs-site" / "src" / "content" / "docs" / "commands.md"


def main() -> None:
    clear_commands()
    register_builtin_commands()
    commands = sorted(list_commands(), key=lambda command: command.name)
    by_namespace: dict[str, list] = defaultdict(list)
    for command in commands:
        namespace = command.name.split(".", 1)[0]
        by_namespace[namespace].append(command)

    lines = [
        "---",
        "title: Commands",
        "description: Generated command reference for Finance CLI.",
        "---",
        "",
        "# Commands",
        "",
        "This page is generated from the Finance CLI command registry.",
        "",
        "Run `python scripts/generate_cli_docs.py` after changing command metadata.",
        "",
    ]
    for namespace in sorted(by_namespace):
        lines.extend([f"## `{namespace}.*`", ""])
        for command in by_namespace[namespace]:
            lines.extend([f"### `{command.name}`", "", command.summary, ""])
            if command.usage:
                lines.extend(["**Usage**", "", "```bash", f"finance {command.usage}", "```", ""])
            if command.examples:
                lines.extend(["**Examples**", "", "```bash"])
                lines.extend(command.examples)
                lines.extend(["```", ""])
            if command.notes:
                lines.append("**Notes**")
                lines.append("")
                lines.extend(f"- {note}" for note in command.notes)
                lines.append("")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines).rstrip() + "\n")


if __name__ == "__main__":
    main()
