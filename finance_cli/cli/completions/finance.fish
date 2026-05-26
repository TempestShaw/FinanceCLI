function __finance_complete
  set -lx COMP_LINE (commandline -cp)
  set -lx COMP_POINT (string length -- $COMP_LINE)
  finance __complete fish
end
complete -c finance -f -a "(__finance_complete)"
