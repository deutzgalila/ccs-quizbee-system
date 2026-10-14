const { test } = require('node:test');
const assert = require('node:assert/strict');
const { fnv1a, mulberry32, shuffleArray, getContestantOptionMapping: mapping, toCanonicalAnswer, toDisplayedAnswer } = require('../../src/shuffleEngine');
const salt = 'OLFU_QUIZBEE_ITPM311';
const q = Object.freeze({ id: 1, question_type: 'MCQ', options: Object.freeze({ A: 'a', B: 'b', C: 'c', D: 'd' }), correct_answer: 'C' });

test('FNV-1a known vectors and unsigned output', () => {
  assert.equal(fnv1a(''), 2166136261);
  assert.equal(fnv1a('hello'), 0x4f9f2cab);
});
test('Mulberry32 known first value and deterministic bounded stream', () => {
  const a = mulberry32(1), b = mulberry32(1);
  assert.equal(mulberry32(1)(), 0.6270739405881613);
  for (let i = 0; i < 1000; i++) {
    const value = a();
    assert.equal(value, b());
    assert.ok(value >= 0 && value < 1);
  }
});
test('Fisher-Yates copies input and preserves members', () => {
  const input = Object.freeze(['A', 'B', 'C', 'D']);
  assert.deepEqual(shuffleArray(input, () => 0), ['B', 'C', 'D', 'A']);
  assert.deepEqual(shuffleArray([], mulberry32(1)), []);
});
test('1000 mappings are identical and adjacent PIN fixtures differ', () => {
  const expected = mapping(q, 1001, salt);
  for (let i = 0; i < 1000; i++) assert.deepEqual(mapping(q, 1001, salt), expected);
  assert.equal(new Set([1001, 1002, 1003].map(id => JSON.stringify(mapping(q, id, salt).shuffledOptions))).size, 3);
});
test('all letters round-trip and correct answer text stays aligned', () => {
  for (let id = 1; id <= 60; id++) {
    const m = mapping(q, id, salt);
    for (const letter of Object.keys(q.options)) {
      assert.equal(toCanonicalAnswer(q, id, toDisplayedAnswer(q, id, letter, salt), salt), letter);
    }
    assert.equal(m.shuffledOptions[m.displayedCorrectAnswer], q.options.C);
    assert.deepEqual(Object.values(m.shuffledOptions).sort(), Object.values(q.options).sort());
  }
});
test('identification, absent and single options pass through; unknown answers are safe', () => {
  for (const question of [{ ...q, question_type: 'IDENTIFICATION' }, { id: 1 }, { ...q, options: {} }, { ...q, options: { A: 'a' } }]) {
    assert.deepEqual(mapping(question, 1, salt).shuffledOptions, question.options);
    assert.equal(toCanonicalAnswer(question, 1, 'unknown', salt), 'unknown');
  }
  assert.equal(toCanonicalAnswer(q, 1, 'constructor', salt), 'constructor');
  assert.equal(toDisplayedAnswer(q, 1, null, salt), null);
});
test('seed includes question, contestant and salt; option insertion order is irrelevant', () => {
  const base = mapping(q, 1, salt);
  assert.notDeepEqual(mapping({ ...q, id: 2 }, 1, salt), base);
  assert.notDeepEqual(mapping(q, 2, salt), base);
  // Different seeds may legitimately collide among only 24 permutations.
  assert.ok(new Set(Array.from({ length: 20 }, (_, i) => JSON.stringify(mapping(q, 1, `salt-${i}`)))).size > 1);
  assert.deepEqual(mapping({ ...q, options: { D: 'd', C: 'c', B: 'b', A: 'a' } }, 1, salt), base);
});

test('contestant reveal highlights the displayed button and renders option text safely', () => {
  const fs = require('node:fs');
  const vm = require('node:vm');
  const source = fs.readFileSync(require.resolve('../../public/js/contestant.js'), 'utf8');
  const start = source.indexOf('  function handleAnswerReveal(data)');
  const end = source.indexOf('  function showSubmissionStatus', start);
  const buttons = ['A', 'B', 'C', 'D'].map(option => {
    const classes = new Set(option === 'D' ? ['selected'] : []);
    return { dataset: { option }, classList: { add: x => classes.add(x), contains: x => classes.has(x) } };
  });
  const context = {
    elCurrentScore: {}, contestantProfile: {}, currentSubmission: { answer: 'D', pointsAwarded: 0, totalScore: 0 },
    elMcqContainer: null, elIdContainer: null, inputAnswer: null, btnPeekAnswer: null,
    activeQuestion: { question_type: 'MCQ', points: 1 }, mcqOptionButtons: buttons,
    lastSubmittedAnswer: 'D', hasSubmittedCurrent: true, elQuestionCard: {}, window: {},
    showSubmissionStatus: message => { context.message = message; }
  };
  vm.createContext(context);
  vm.runInContext(source.slice(start, end), context);
  context.handleAnswerReveal({ correctAnswer: 'D', correctAnswerText: '<link>', totalScore: 1 });
  assert.ok(buttons[3].classList.contains('is-correct'));
  assert.ok(!buttons[2].classList.contains('is-correct'));
  assert.match(context.message, /<link> \(Option D\)/);
  assert.equal(context.elCurrentScore.textContent, '1 PTS');
  // The production banner writes textContent, never interprets answer text as HTML.
  assert.match(source.slice(end), /elSubmissionStatus\.textContent = msg/);
});
