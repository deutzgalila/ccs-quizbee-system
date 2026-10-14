const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function element() {
  const classes = new Set();
  return { style: {}, textContent: '', classList: {
    add: (...names) => names.forEach(name => classes.add(name)),
    remove: (...names) => names.forEach(name => classes.delete(name)),
    contains: name => classes.has(name)
  } };
}
function fixture() {
  const source = fs.readFileSync(require.resolve('../../public/js/contestant.js'), 'utf8');
  const nodes = {};
  for (const letter of ['A', 'B', 'C', 'D']) {
    nodes[`opt-${letter.toLowerCase()}`] = { ...element(), dataset: { option: letter } };
    nodes[`text-opt-${letter.toLowerCase()}`] = element();
  }
  const context = {
    document: { getElementById: id => nodes[id] }, currentPhase: 'READING',
    mcqOptionButtons: ['a', 'b', 'c', 'd'].map(letter => nodes[`opt-${letter}`]),
    updateTimer() {}, showSubmissionStatus() {}, window: {}, contestantProfile: {}
  };
  for (const name of ['elQuestionCard', 'elSubmissionStatus', 'elRoundBadge', 'elItemBadge',
    'elPointBadge', 'elQuestionText', 'elCodeSnippet', 'elCodeContent', 'elCountdownNotice',
    'elMcqContainer', 'elIdContainer', 'btnPeekAnswer', 'inputAnswer', 'elCurrentScore']) context[name] = element();
  vm.createContext(context);
  for (const [start, end] of [['  function renderQuestion(q)', '  function updateTimer'],
    ['  function handleAnswerReveal(data)', '  function showSubmissionStatus']]) {
    vm.runInContext(source.slice(source.indexOf(start), source.indexOf(end)), context);
  }
  return { context, nodes };
}
const question = { question_type: 'MCQ', options: { A: 'Jake', B: 'Jane', C: 'John', D: 'Jill' }, points: 1 };

test('render reorders existing buttons while preserving label, text and reveal target', () => {
  const { context, nodes } = fixture();
  const buttonA = nodes['opt-a'];
  context.renderQuestion({ ...question, display_order: ['B', 'C', 'A', 'D'] });
  assert.equal(buttonA.style.order, 3);
  assert.equal(nodes['opt-b'].style.order, 1);
  assert.equal(nodes['opt-c'].style.order, 2);
  assert.equal(buttonA.dataset.option, 'A');
  for (const [letter, text] of Object.entries(question.options)) assert.equal(nodes[`text-opt-${letter.toLowerCase()}`].textContent, text);
  context.hasSubmittedCurrent = true;
  context.lastSubmittedAnswer = 'A';
  buttonA.classList.add('selected');
  context.handleAnswerReveal({ correctAnswer: 'A' });
  assert.ok(buttonA.classList.contains('is-correct'));
  assert.equal(buttonA.style.order, 3);
  assert.ok(!nodes['opt-c'].classList.contains('is-correct'));
  assert.equal(nodes['opt-a'], buttonA);
});

test('later questions reset previous ordering and tolerate missing letters', () => {
  const { context, nodes } = fixture();
  context.renderQuestion({ ...question, display_order: ['D', 'C', 'B', 'A'] });
  assert.equal(nodes['opt-a'].style.order, 4);
  context.renderQuestion(question);
  for (const [i, letter] of ['a', 'b', 'c', 'd'].entries()) assert.equal(nodes[`opt-${letter}`].style.order, i + 1);
  context.renderQuestion({ ...question, display_order: ['B', 'A'] });
  assert.equal(nodes['opt-d'].style.order, 0);
  context.renderQuestion({ question_type: 'IDENTIFICATION', question: 'Name Jake' });
  assert.ok(context.elMcqContainer.classList.contains('hidden'));
  context.renderQuestion(question);
  assert.equal(nodes['opt-a'].style.order, 1);
});
