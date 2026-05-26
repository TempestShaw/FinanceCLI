# CLI Shell Completions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add global shell completion for `finance` so users can tab-complete namespaces, commands, global options, output values, command argument keys, and enum/default values without memorizing the CLI surface.

**Architecture:** Implement a small FinanceCLI-owned completion protocol instead of binding command execution to a third-party completion framework. Shell scripts call a hidden `finance __complete SHELL` entrypoint; that entrypoint inspects the current command line, reads the live command registry plus package-owned usage metadata, and returns suggestions without running command handlers or making network calls. Completion metadata must be derived from the same registry/usage parsing used for generated docs so command docs, agent schemas, and completions cannot drift independently.

**Tech Stack:** Python `argparse`, FinanceCLI command registry, `shlex`, package-owned usage parser, bash/zsh/fish completion scripts, pytest.

---

## Decisions Locked

- Do not execute command handlers during completion.
- Do not make network calls during completion.
- Do not maintain a second hardcoded list of commands.
- Support bash, zsh, and fish via `finance completion bash|zsh|fish`.
- Add hidden `finance __complete SHELL` for shell wrappers.
- Completion should work for partial tokens:
  - `finance sou<TAB>` suggests `sources.`
  - `finance sources.<TAB>` suggests `sources.list`, `sources.status`, `sources.test`
  - `finance sources.sta<TAB>` suggests `sources.status`
  - `finance --outp<TAB>` suggests `--output`
  - `finance market.quote AAPL --outp<TAB>` suggests `--output`
  - `finance --output <TAB>` suggests output formats.
  - `finance document.scan file.pdf format=<TAB>` suggests `format=pdf` and `format=html`.
- Completion should prefer command and option metadata over fuzzy guessing. No ticker search, no filesystem crawl beyond shell-native filename completion.
- For positional symbols, paths, and free text, return no FinanceCLI suggestions and let the shell fallback handle files when possible.

## Success Criteria

- `finance completion bash`, `finance completion zsh`, and `finance completion fish` print shell scripts.
- The scripts call `finance __complete <shell>` and do not embed a stale command list.
- Hidden completion returns newline-delimited suggestions for bash/zsh and fish-safe suggestions for fish.
- Command namespace completion works for `sources.`, `sources.sta`, and top-level namespace prefixes.
- Global option completion works before and after the command token.
- Global option value completion works for `--output`.
- Command argument key completion works from `FinanceCommand.usage` metadata.
- Enum value completion works for usage tokens such as `format=pdf|html`, `statement=income|balance|cashflow`, and `table=top_companies|top_etfs`.
- Generated docs and `tools.json` include the visible `completion` command.
- Full test suite passes.

## File Structure

- Create `finance_cli/cli/usage.py`: package-owned parser for `FinanceCommand.usage` strings. Move or mirror the doc generator usage parsing behavior here.
- Modify `scripts/generate_cli_docs.py`: import the new usage parser instead of keeping the parser private to the script.
- Create `finance_cli/cli/options.py`: shared global CLI option/output metadata used by argparse and completion.
- Create `finance_cli/cli/completion.py`: completion data model, shell token context parser, command/option/argument candidate generation, and shell script renderers.
- Create `finance_cli/cli/commands/completion.py`: visible `completion` command that prints bash/zsh/fish scripts.
- Modify `finance_cli/cli/commands/__init__.py`: register the visible completion command.
- Modify `finance_cli/cli/main.py`: intercept hidden `__complete` before normal argparse parsing.
- Modify `tests/test_cli_smoke.py`: CLI-level completion protocol and generated schema coverage.
- Create `tests/test_cli_completion.py`: focused unit tests for completion parsing and suggestions.
- Modify `README.md`, `EXAMPLES.md`, and generated docs through `python scripts/generate_cli_docs.py`.

---

### Task 1: Package-Owned Usage Parser

**Files:**
- Create: `finance_cli/cli/usage.py`
- Modify: `scripts/generate_cli_docs.py`
- Test: `tests/test_cli_completion.py`
- Test: `tests/test_cli_smoke.py`

- [ ] **Step 1: Write failing tests for usage parsing**

Create `tests/test_cli_completion.py` with:

```python
from finance_cli.cli.usage import parse_usage_params


def test_parse_usage_params_extracts_keys_required_flags_and_enums():
    params = parse_usage_params(
        "document.scan SOURCE|source=PATH_OR_URL "
        "[query=TEXT format=pdf|html match=fuzzy|all_terms max_chars=12000]"
    )

    assert params["source"]["required"] is True
    assert params["source"]["aliases"] == ["SOURCE"]
    assert params["format"]["enum"] == ["pdf", "html"]
    assert params["match"]["enum"] == ["fuzzy", "all_terms"]
    assert params["max_chars"]["default"] == 12000
```

Add a generator smoke assertion in `tests/test_cli_smoke.py`:

```python
def test_generated_specs_use_package_usage_parser():
    from finance_cli.cli.usage import parse_usage_params

    params = parse_usage_params("price.moves SYMBOL [window=1d|3d|1w|1m limit=20]")

    assert params["window"]["enum"] == ["1d", "3d", "1w", "1m"]
    assert params["limit"]["default"] == 20
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest -q tests/test_cli_completion.py::test_parse_usage_params_extracts_keys_required_flags_and_enums tests/test_cli_smoke.py::test_generated_specs_use_package_usage_parser
```

Expected: FAIL with `ModuleNotFoundError: No module named 'finance_cli.cli.usage'`.

- [ ] **Step 3: Implement `finance_cli/cli/usage.py`**

Add:

```python
"""Parse FinanceCommand usage strings for docs and shell completion."""
from __future__ import annotations

import re
import shlex
from typing import Any


def parse_usage_params(usage: str) -> dict[str, dict[str, Any]]:
    if not usage:
        return {}
    parts = _split_usage(usage)
    if parts and not parts[0][1]:
        parts = parts[1:]
    params: dict[str, dict[str, Any]] = {}
    for token, optional in parts:
        parsed = _parse_token(token, optional=optional)
        if parsed is None:
            continue
        name, meta = parsed
        if name in params:
            params[name] = {**params[name], **meta}
            params[name]["required"] = params[name].get("required", False) or meta.get("required", False)
        else:
            params[name] = meta
    return params


def _split_usage(usage: str) -> list[tuple[str, bool]]:
    tokens: list[tuple[str, bool]] = []
    current: list[str] = []
    optional = False
    for char in usage:
        if char == "[" and not optional:
            if current:
                tokens.extend((part, optional) for part in _shell_split("".join(current)))
                current = []
            optional = True
            continue
        if char == "]" and optional:
            if current:
                tokens.extend((part, True) for part in _shell_split("".join(current)))
                current = []
            optional = False
            continue
        current.append(char)
    if current:
        tokens.extend((part, optional) for part in _shell_split("".join(current)))
    return tokens


def _shell_split(text: str) -> list[str]:
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()


def _parse_token(token: str, *, optional: bool) -> tuple[str, dict[str, Any]] | None:
    token = token.strip()
    if not token or token.startswith("--"):
        return None
    if token.startswith("(") or token.endswith(")"):
        return None
    if "=" in token:
        raw_name, raw_value = token.split("=", 1)
        aliases = [_clean_name(part) for part in raw_name.split("|") if _clean_name(part)]
        if not aliases:
            return None
        meta = _value_meta(raw_value, required=not optional)
        if len(aliases) > 1:
            meta["aliases"] = aliases[:-1]
        return aliases[-1], meta
    if "|" in token:
        aliases = [_clean_name(part) for part in token.split("|") if _clean_name(part)]
        if not aliases:
            return None
        meta = {"required": not optional}
        if len(aliases) > 1:
            meta["aliases"] = aliases[:-1]
        return aliases[-1], meta
    name = _clean_name(token)
    if not name:
        return None
    return name, {"required": not optional}


def _value_meta(raw_value: str, *, required: bool) -> dict[str, Any]:
    meta: dict[str, Any] = {"required": required}
    values = [part for part in raw_value.split("|") if part]
    if len(values) > 1:
        meta["enum"] = values
    elif values:
        default = _literal_default(values[0])
        if default is not None:
            meta["default"] = default
    return meta


def _literal_default(value: str) -> Any:
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.isupper() or value in {"TEXT", "PATH_OR_URL", "YYYY-MM-DD", "URL"}:
        return None
    return value


def _clean_name(value: str) -> str:
    return value.strip("<>[](),")
```

- [ ] **Step 4: Update docs generator to import parser**

In `scripts/generate_cli_docs.py`, replace private `_parse_usage_params(...)` calls with:

```python
from finance_cli.cli.usage import parse_usage_params
```

and change:

```python
params = _parse_usage_params(command.usage)
```

to:

```python
params = parse_usage_params(command.usage)
```

Remove the old private parser helpers only after tests pass; keep unrelated generator logic untouched.

- [ ] **Step 5: Run focused tests**

Run:

```bash
python -m pytest -q tests/test_cli_completion.py::test_parse_usage_params_extracts_keys_required_flags_and_enums tests/test_cli_smoke.py::test_generated_specs_use_package_usage_parser tests/test_cli_smoke.py::test_generated_agent_schema_covers_registered_commands
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add finance_cli/cli/usage.py scripts/generate_cli_docs.py tests/test_cli_completion.py tests/test_cli_smoke.py
git commit -m "refactor: share CLI usage metadata parser"
```

---

### Task 2: Completion Engine

**Files:**
- Create: `finance_cli/cli/options.py`
- Create: `finance_cli/cli/completion.py`
- Modify: `finance_cli/cli/main.py`
- Test: `tests/test_cli_completion.py`

- [ ] **Step 1: Write failing tests for command and option suggestions**

Append to `tests/test_cli_completion.py`:

```python
from finance_cli.cli.commands import register_builtin_commands
from finance_cli.cli.completion import complete
from finance_cli.cli.registry import clear_commands


def registered_completions(line: str) -> list[str]:
    clear_commands()
    register_builtin_commands()
    return complete(line, len(line))


def test_completion_suggests_namespaces_and_commands():
    assert "sources." in registered_completions("finance sou")
    assert "sources.status" in registered_completions("finance sources.sta")
    assert {"sources.list", "sources.status", "sources.test"}.issubset(
        set(registered_completions("finance sources."))
    )


def test_completion_suggests_global_options_anywhere():
    assert "--output" in registered_completions("finance --outp")
    assert "--output" in registered_completions("finance market.quote AAPL --outp")


def test_completion_suggests_output_values_after_output_option():
    suggestions = registered_completions("finance market.quote AAPL --output ")

    assert {"json", "compact", "schema"}.issubset(set(suggestions))


def test_completion_suggests_key_value_arguments_and_enum_values():
    assert "format=" in registered_completions("finance document.scan sample.pdf for")

    suggestions = registered_completions("finance document.scan sample.pdf format=")

    assert "format=pdf" in suggestions
    assert "format=html" in suggestions
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest -q tests/test_cli_completion.py -k "completion_suggests"
```

Expected: FAIL with `ModuleNotFoundError: No module named 'finance_cli.cli.completion'`.

- [ ] **Step 3: Implement completion engine**

Create `finance_cli/cli/options.py`:

```python
"""Shared global CLI option metadata."""
from __future__ import annotations

OUTPUT_FORMATS = ("json", "text", "compact", "schema")

GLOBAL_OPTIONS = {
    "--output": list(OUTPUT_FORMATS),
    "--fields": [],
    "--max-records": [],
    "--max-chars": [],
    "--list": [],
    "--help": [],
}
```

Modify `finance_cli/cli/main.py` so argparse uses the shared values:

```python
from finance_cli.cli.options import OUTPUT_FORMATS

# inside build_parser()
parser.add_argument("--output", choices=OUTPUT_FORMATS, default="json")
```

Create `finance_cli/cli/completion.py`:

```python
"""FinanceCLI shell completion engine."""
from __future__ import annotations

import shlex
from dataclasses import dataclass

from finance_cli.cli.options import GLOBAL_OPTIONS
from finance_cli.cli.registry import FinanceCommand, list_commands
from finance_cli.cli.usage import parse_usage_params


@dataclass(frozen=True)
class CompletionContext:
    words: tuple[str, ...]
    current: str


def complete(line: str, point: int | None = None) -> list[str]:
    context = _context(line, point)
    command = _selected_command(context.words)
    if _previous_word(context.words) == "--output":
        return _prefix_filter(GLOBAL_OPTIONS["--output"], context.current)
    if context.current.startswith("--"):
        return _prefix_filter(list(GLOBAL_OPTIONS), context.current)
    if "=" in context.current and command is not None:
        return _complete_key_value(command, context.current)
    if command is not None:
        command_args = _command_arg_suggestions(command, context.current)
        if command_args:
            return command_args
        return _prefix_filter(list(GLOBAL_OPTIONS), context.current)
    return _complete_command_or_namespace(context.current)


def _context(line: str, point: int | None) -> CompletionContext:
    left = line[: point if point is not None else len(line)]
    ends_with_space = left.endswith((" ", "\t"))
    words = tuple(_safe_split(left))
    if not words:
        return CompletionContext(words=(), current="")
    if ends_with_space:
        return CompletionContext(words=words, current="")
    return CompletionContext(words=words[:-1], current=words[-1])


def _safe_split(text: str) -> list[str]:
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()


def _previous_word(words: tuple[str, ...]) -> str | None:
    return words[-1] if words else None


def _selected_command(words: tuple[str, ...]) -> FinanceCommand | None:
    commands = {command.name: command for command in list_commands()}
    for word in words:
        if word in commands:
            return commands[word]
    return None


def _complete_command_or_namespace(prefix: str) -> list[str]:
    names = sorted(command.name for command in list_commands())
    namespaces = sorted({name.split(".", 1)[0] + "." for name in names if "." in name})
    if "." not in prefix:
        return _prefix_filter(namespaces + names, prefix)
    return _prefix_filter(names, prefix)


def _command_arg_suggestions(command: FinanceCommand, prefix: str) -> list[str]:
    params = parse_usage_params(command.usage)
    keys = sorted(f"{name}=" for name in params if not name.isupper())
    return _prefix_filter(keys, prefix)


def _complete_key_value(command: FinanceCommand, current: str) -> list[str]:
    key, value_prefix = current.split("=", 1)
    params = parse_usage_params(command.usage)
    meta = params.get(key)
    if not meta:
        return []
    values = [f"{key}={value}" for value in meta.get("enum", [])]
    return _prefix_filter(values, f"{key}={value_prefix}")


def _prefix_filter(values: list[str], prefix: str) -> list[str]:
    return [value for value in values if value.startswith(prefix)]
```

- [ ] **Step 4: Run focused tests**

Run:

```bash
python -m pytest -q tests/test_cli_completion.py -k "completion_suggests"
```

Expected: PASS.

- [ ] **Step 5: Add no-handler-execution regression test**

Append:

```python
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult


def test_completion_does_not_execute_command_handlers():
    clear_commands()

    def fail_if_called(_args: list[str]) -> FinanceCommandResult:
        raise AssertionError("completion must not run command handlers")

    register_command(FinanceCommand("custom.status", "Custom status", fail_if_called, usage="custom.status [mode=fast|full]"))

    assert complete("finance custom.status mode=", len("finance custom.status mode=")) == ["mode=fast", "mode=full"]
```

Run:

```bash
python -m pytest -q tests/test_cli_completion.py::test_completion_does_not_execute_command_handlers
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add finance_cli/cli/options.py finance_cli/cli/completion.py finance_cli/cli/main.py tests/test_cli_completion.py
git commit -m "feat: add CLI completion engine"
```

---

### Task 3: Hidden Completion Entrypoint

**Files:**
- Modify: `finance_cli/cli/main.py`
- Test: `tests/test_cli_completion.py`

- [ ] **Step 1: Write failing CLI protocol tests**

Append to `tests/test_cli_completion.py`:

```python
from finance_cli.cli.main import main


def test_hidden_complete_entrypoint_prints_suggestions(capsys, monkeypatch):
    monkeypatch.setenv("COMP_LINE", "finance sources.sta")
    monkeypatch.setenv("COMP_POINT", str(len("finance sources.sta")))

    code = main(["__complete", "bash"])
    output = capsys.readouterr().out.strip().splitlines()

    assert code == 0
    assert "sources.status" in output


def test_hidden_complete_entrypoint_rejects_unknown_shell(capsys, monkeypatch):
    monkeypatch.setenv("COMP_LINE", "finance sources.")
    monkeypatch.setenv("COMP_POINT", str(len("finance sources.")))

    code = main(["__complete", "powershell"])
    output = capsys.readouterr().out

    assert code == 2
    assert "unknown completion shell" in output
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest -q tests/test_cli_completion.py -k "hidden_complete"
```

Expected: FAIL because `__complete` is treated as an unknown command.

- [ ] **Step 3: Add shell formatting helpers**

In `finance_cli/cli/completion.py`, add:

```python
SUPPORTED_SHELLS = {"bash", "zsh", "fish"}


def complete_from_env(shell: str, env: dict[str, str]) -> tuple[int, str]:
    if shell not in SUPPORTED_SHELLS:
        return 2, f"unknown completion shell: {shell}"
    line = env.get("COMP_LINE", "")
    try:
        point = int(env.get("COMP_POINT", str(len(line))))
    except ValueError:
        point = len(line)
    suggestions = complete(line, point)
    return 0, "\n".join(_format_suggestion(shell, suggestion) for suggestion in suggestions)


def _format_suggestion(shell: str, suggestion: str) -> str:
    if shell == "fish":
        return suggestion.replace("\\t", " ")
    return suggestion
```

- [ ] **Step 4: Intercept hidden command in `main.py`**

In `finance_cli/cli/main.py`, before help handling, add:

```python
    if raw_args and raw_args[0] == "__complete":
        from finance_cli.cli.completion import complete_from_env

        shell = raw_args[1] if len(raw_args) > 1 else "bash"
        code, output = complete_from_env(shell, dict(os.environ))
        if output:
            print(output)
        return code
```

Add `import os` at the top of `finance_cli/cli/main.py`.

- [ ] **Step 5: Run focused tests**

Run:

```bash
python -m pytest -q tests/test_cli_completion.py -k "hidden_complete"
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add finance_cli/cli/main.py finance_cli/cli/completion.py tests/test_cli_completion.py
git commit -m "feat: add hidden completion protocol"
```

---

### Task 4: Shell Script Command

**Files:**
- Create: `finance_cli/cli/commands/completion.py`
- Modify: `finance_cli/cli/commands/__init__.py`
- Test: `tests/test_cli_completion.py`
- Test: `tests/test_cli_smoke.py`

- [ ] **Step 1: Write failing tests for visible completion command**

Append to `tests/test_cli_completion.py`:

```python
def test_completion_command_prints_bash_script(capsys):
    code = main(["completion", "bash"])
    output = capsys.readouterr().out

    assert code == 0
    assert "_finance_complete" in output
    assert "finance __complete bash" in output


def test_completion_command_prints_zsh_script(capsys):
    code = main(["completion", "zsh"])
    output = capsys.readouterr().out

    assert code == 0
    assert "#compdef finance" in output
    assert "finance __complete zsh" in output


def test_completion_command_prints_fish_script(capsys):
    code = main(["completion", "fish"])
    output = capsys.readouterr().out

    assert code == 0
    assert "complete -c finance" in output
    assert "finance __complete fish" in output
```

Add to `tests/test_cli_smoke.py`:

```python
def test_completion_command_is_registered():
    clear_commands()
    register_builtin_commands()

    names = {command.name for command in list_commands()}

    assert "completion" in names
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest -q tests/test_cli_completion.py -k "completion_command_prints" tests/test_cli_smoke.py::test_completion_command_is_registered
```

Expected: FAIL because the visible command is not registered.

- [ ] **Step 3: Implement shell script renderers**

In `finance_cli/cli/completion.py`, add:

```python
def completion_script(shell: str) -> str:
    if shell == "bash":
        return BASH_SCRIPT.strip() + "\n"
    if shell == "zsh":
        return ZSH_SCRIPT.strip() + "\n"
    if shell == "fish":
        return FISH_SCRIPT.strip() + "\n"
    raise ValueError(f"unknown completion shell: {shell}")


BASH_SCRIPT = r'''
_finance_complete() {
  local IFS=$'\n'
  COMPREPLY=($(COMP_LINE="$COMP_LINE" COMP_POINT="$COMP_POINT" finance __complete bash))
}
complete -o default -F _finance_complete finance
'''


ZSH_SCRIPT = r'''
#compdef finance
_finance_complete() {
  local -a completions
  completions=("${(@f)$(COMP_LINE="$BUFFER" COMP_POINT="$CURSOR" finance __complete zsh)}")
  compadd -- "${completions[@]}"
}
compdef _finance_complete finance
'''


FISH_SCRIPT = r'''
function __finance_complete
  set -lx COMP_LINE (commandline -cp)
  set -lx COMP_POINT (string length -- $COMP_LINE)
  finance __complete fish
end
complete -c finance -f -a "(__finance_complete)"
'''
```

- [ ] **Step 4: Register visible command**

Create `finance_cli/cli/commands/completion.py`:

```python
"""Shell completion CLI command."""
from __future__ import annotations

from finance_cli.cli.completion import completion_script
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult


def _completion(args: list[str]) -> FinanceCommandResult:
    shell = args[0] if args else "bash"
    try:
        script = completion_script(shell)
    except ValueError as exc:
        return FinanceCommandResult(ok=False, error=str(exc))
    return FinanceCommandResult(ok=True, data={"shell": shell, "script": script})


def register_completion_commands() -> None:
    register_command(FinanceCommand(
        "completion",
        "Print shell completion setup for bash, zsh, or fish",
        _completion,
        usage="completion SHELL",
        examples=(
            "finance completion bash > ~/.local/share/bash-completion/completions/finance",
            "finance completion zsh > ~/.zfunc/_finance",
            "finance completion fish > ~/.config/fish/completions/finance.fish",
        ),
        notes=(
            "Prints shell code only; it does not modify shell startup files.",
            "Completion candidates are generated from the live command registry and usage metadata.",
        ),
    ))
```

Modify `finance_cli/cli/commands/__init__.py`:

```python
from finance_cli.cli.commands.completion import register_completion_commands
```

and call it early in `register_builtin_commands()`:

```python
    register_completion_commands()
```

- [ ] **Step 5: Render script payload as raw text**

In `finance_cli/cli/formatting.py`, add a special report/text rule only for completion scripts:

```python
    if command == "completion" and result.ok and isinstance(result.data, dict) and isinstance(result.data.get("script"), str):
        return result.data["script"].rstrip()
```

Place it before JSON/text/record rendering so `finance completion bash` prints executable shell code by default.

- [ ] **Step 6: Run focused tests**

Run:

```bash
python -m pytest -q tests/test_cli_completion.py -k "completion_command_prints" tests/test_cli_smoke.py::test_completion_command_is_registered
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```bash
git add finance_cli/cli/completion.py finance_cli/cli/commands/completion.py finance_cli/cli/commands/__init__.py finance_cli/cli/formatting.py tests/test_cli_completion.py tests/test_cli_smoke.py
git commit -m "feat: add shell completion scripts"
```

---

### Task 5: Docs And Generated Metadata

**Files:**
- Modify: `README.md`
- Modify: `EXAMPLES.md`
- Modify generated: `tools.json`
- Modify generated: `openapi.json`
- Modify generated: `llms.txt`
- Modify generated: `llms-full.txt`
- Modify generated: `docs-site/public/tools.json`
- Modify generated: `docs-site/public/openapi.json`
- Modify generated: `docs-site/public/llms.txt`
- Modify generated: `docs-site/public/llms-full.txt`
- Modify generated: `docs-site/src/content/docs/commands.md`
- Test: `tests/test_cli_smoke.py`

- [ ] **Step 1: Write failing metadata assertion**

In `tests/test_cli_smoke.py`, extend `test_generated_agent_schema_covers_registered_commands`:

```python
    completion = next(spec for spec in specs if spec["name"] == "completion")
    assert completion["args"]["SHELL"]["required"] is True
    assert "shell completion setup" in completion["summary"].lower()
```

- [ ] **Step 2: Run test and verify failure if metadata is missing**

Run:

```bash
python -m pytest -q tests/test_cli_smoke.py::test_generated_agent_schema_covers_registered_commands
```

Expected: FAIL until `completion` is registered and usage metadata is visible.

- [ ] **Step 3: Update README and EXAMPLES**

Add to `README.md`:

````markdown
### Shell Completion

FinanceCLI can print shell completion scripts without modifying your shell files:

```bash
finance completion bash > ~/.local/share/bash-completion/completions/finance
finance completion zsh > ~/.zfunc/_finance
finance completion fish > ~/.config/fish/completions/finance.fish
```

Completions are generated from the live command registry and usage metadata, so command names, global options, and key=value argument enums stay aligned with the CLI.
````

Add the same short examples to `EXAMPLES.md`.

- [ ] **Step 4: Regenerate docs**

Run:

```bash
python scripts/generate_cli_docs.py
```

- [ ] **Step 5: Run focused tests and metadata grep**

Run:

```bash
python -m pytest -q tests/test_cli_smoke.py::test_generated_agent_schema_covers_registered_commands
rg -n '"name": "completion"|finance completion bash|__complete' tools.json openapi.json llms.txt llms-full.txt docs-site/public docs-site/src/content/docs/commands.md
```

Expected: test passes and grep finds completion docs.

- [ ] **Step 6: Commit**

Run:

```bash
git add README.md EXAMPLES.md tools.json openapi.json llms.txt llms-full.txt docs-site/public docs-site/src/content/docs/commands.md tests/test_cli_smoke.py
git commit -m "docs: document shell completions"
```

---

### Task 6: Verification And Review

**Files:**
- No production edits expected unless verification fails.

- [ ] **Step 1: Run focused completion tests**

Run:

```bash
python -m pytest -q tests/test_cli_completion.py tests/test_cli_smoke.py::test_generated_agent_schema_covers_registered_commands
```

Expected: PASS.

- [ ] **Step 2: Run full Python test suite**

Run:

```bash
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 3: Run generated docs/site checks**

Run:

```bash
git diff --check
cd docs-site && npm run build
```

Expected: PASS.

- [ ] **Step 4: Manual CLI smoke checks**

Run:

```bash
COMP_LINE="finance sources." COMP_POINT=16 finance __complete bash
COMP_LINE="finance sources.sta" COMP_POINT=19 finance __complete bash
COMP_LINE="finance market.quote AAPL --outp" COMP_POINT=32 finance __complete bash
COMP_LINE="finance document.scan sample.pdf format=" COMP_POINT=40 finance __complete bash
finance completion bash | rg "finance __complete bash"
finance completion zsh | rg "finance __complete zsh"
finance completion fish | rg "finance __complete fish"
```

Expected output includes:

```text
sources.list
sources.status
sources.test
sources.status
--output
format=pdf
format=html
```

- [ ] **Step 5: External review**

Run one of:

```bash
gemini --yolo "Review the FinanceCLI shell completion implementation for command registry drift, shell quoting bugs, accidental command execution during completion, generated metadata alignment, and missing tests."
```

or:

```bash
claude --dangerously-skip-permissions "Review the FinanceCLI shell completion implementation for command registry drift, shell quoting bugs, accidental command execution during completion, generated metadata alignment, and missing tests. Return only actionable issues with file/function references."
```

Allow up to 5 minutes. Fix actionable issues before final verification.

- [ ] **Step 6: Final status**

Run:

```bash
git status -sb
git log --oneline -5
```

Expected: branch contains only shell completion commits and intended generated artifacts.

