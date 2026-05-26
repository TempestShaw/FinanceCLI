#compdef finance
_finance_complete() {
  local -a completions
  completions=("${(@f)$(COMP_LINE="$BUFFER" COMP_POINT="$CURSOR" finance __complete zsh)}")
  compadd -- "${completions[@]}"
}
compdef _finance_complete finance
