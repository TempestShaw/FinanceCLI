_finance_complete() {
  local IFS=$'\n'
  COMPREPLY=($(COMP_LINE="$COMP_LINE" COMP_POINT="$COMP_POINT" finance __complete bash))
}
complete -o default -F _finance_complete finance
