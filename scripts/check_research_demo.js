// Open the built homepage, then: agent-browser eval --stdin < scripts/check_research_demo.js
(async () => {
  const demo = document.querySelector('[data-research-demo]');
  const toggle = demo.querySelector('[data-toggle]');
  const replay = demo.querySelector('[data-replay]');
  const steps = [...demo.querySelectorAll('[data-step]')];
  const visible = () => steps.filter(step => !step.hidden).length;
  const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  replay.click();
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    assert(visible() === 3 && toggle.disabled, 'Reduced motion must show complete result');
    assert(getComputedStyle(steps[0]).animationName === 'none', 'Reduced motion must not animate');
    return 'PASS: reduced-motion static result and replay';
  }
  assert(visible() === 1, 'Replay must restart from step one');
  toggle.click();
  await wait(2900);
  assert(visible() === 1 && toggle.textContent === 'Resume', 'Pause must stop progress');
  toggle.click();
  await wait(2800);
  assert(visible() === 2, 'Resume must advance to step two');
  await wait(2800);
  assert(visible() === 3 && toggle.disabled, 'Playback must finish without looping');
  assert(demo.querySelector('[data-progress]').textContent === 'Example complete', 'Completion status');
  const details = demo.querySelector('details');
  details.open = true;
  assert(details.textContent.includes('0000320193-25-000079'), 'Recorded filing identity is required');
  details.open = false;
  return 'PASS: replay, pause, resume, completion, and source details';
})();
