#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF'
Usage: scripts/install_completion.sh [zsh|bash|fish]

Installs FinanceCLI shell completion for the selected shell. If no shell is
provided, the script uses the current SHELL basename.

Environment overrides:
  FINANCE_CMD                 FinanceCLI command to run. Default: finance
  FINANCE_ZSH_COMPLETION_DIR  zsh completion dir. Default: ~/.zfunc
  FINANCE_ZSHRC               zsh startup file. Default: ~/.zshrc
  FINANCE_BASH_COMPLETION_DIR bash completion dir. Default: ~/.local/share/bash-completion/completions
  FINANCE_BASHRC              bash startup file. Default: ~/.bashrc
  FINANCE_FISH_COMPLETION_DIR fish completion dir. Default: ~/.config/fish/completions
EOF
}

finance_cmd=${FINANCE_CMD:-finance}
shell_name=${1:-${SHELL##*/}}

run_finance_completion() {
  # Intentionally allows FINANCE_CMD="python -m finance_cli.cli.main" for tests
  # and editable checkouts.
  # shellcheck disable=SC2086
  $finance_cmd completion "$1"
}

append_once() {
  file=$1
  marker=$2
  block=$3
  touch "$file"
  if grep -Fq "$marker" "$file"; then
    return 0
  fi
  {
    printf '\n'
    printf '%s\n' "$block"
  } >> "$file"
}

install_zsh() {
  completion_dir=${FINANCE_ZSH_COMPLETION_DIR:-"$HOME/.zfunc"}
  rc_file=${FINANCE_ZSHRC:-"$HOME/.zshrc"}
  mkdir -p "$completion_dir"
  run_finance_completion zsh > "$completion_dir/_finance"
  append_once "$rc_file" "# BEGIN FinanceCLI completion" "# BEGIN FinanceCLI completion
fpath=(\"$completion_dir\" \$fpath)
autoload -Uz compinit
compinit -i
[ -s \"$completion_dir/_finance\" ] && source \"$completion_dir/_finance\"
# END FinanceCLI completion"
  printf 'Installed FinanceCLI zsh completion at %s/_finance\n' "$completion_dir"
  printf 'Restart zsh or run: source %s\n' "$rc_file"
}

install_bash() {
  completion_dir=${FINANCE_BASH_COMPLETION_DIR:-"$HOME/.local/share/bash-completion/completions"}
  rc_file=${FINANCE_BASHRC:-"$HOME/.bashrc"}
  mkdir -p "$completion_dir"
  run_finance_completion bash > "$completion_dir/finance"
  append_once "$rc_file" "# BEGIN FinanceCLI completion" "# BEGIN FinanceCLI completion
[ -s \"$completion_dir/finance\" ] && . \"$completion_dir/finance\"
# END FinanceCLI completion"
  printf 'Installed FinanceCLI bash completion at %s/finance\n' "$completion_dir"
  printf 'Restart bash or run: source %s\n' "$rc_file"
}

install_fish() {
  completion_dir=${FINANCE_FISH_COMPLETION_DIR:-"$HOME/.config/fish/completions"}
  mkdir -p "$completion_dir"
  run_finance_completion fish > "$completion_dir/finance.fish"
  printf 'Installed FinanceCLI fish completion at %s/finance.fish\n' "$completion_dir"
  printf 'Restart fish or run: source %s/finance.fish\n' "$completion_dir"
}

case "$shell_name" in
  zsh)
    install_zsh
    ;;
  bash)
    install_bash
    ;;
  fish)
    install_fish
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    printf 'Unsupported shell: %s\n\n' "$shell_name" >&2
    usage >&2
    exit 2
    ;;
esac
