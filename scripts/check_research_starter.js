// Open the built homepage with agent-browser, then run:
// agent-browser eval --stdin < scripts/check_research_starter.js
(() => {
  const form = document.querySelector('#research-starter');
  const output = document.querySelector('#research-command');
  const symbol = form.elements.symbol;
  const question = form.elements.question;
  for (const [task, command] of [
    ['business', 'finance filings.read MSFT section=business max_chars=4000 --output md'],
    ['risks', 'finance filings.read MSFT section=risk_factors max_chars=4000 --output md'],
    ['filings', 'finance filings.recent MSFT forms=10-K,10-Q limit=3 --output md'],
  ]) {
    symbol.value = 'msft';
    question.value = task;
    form.requestSubmit();
    if (output.textContent !== command) throw new Error(`Wrong command for ${task}`);
  }
  const previous = output.textContent;
  for (const invalid of ['', 'AAPL;pwd', '$(whoami)']) {
    symbol.value = invalid;
    if (form.checkValidity()) throw new Error('Invalid ticker accepted');
    form.requestSubmit();
    if (output.textContent !== previous) throw new Error('Invalid ticker changed command');
  }
  symbol.value = 'AAPL';
  question.value = 'business';
  form.requestSubmit();
  return 'PASS: three research tasks, ticker normalization, invalid input';
})();
