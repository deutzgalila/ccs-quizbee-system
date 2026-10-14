const { test } = require('node:test');
const assert = require('node:assert/strict');
const { fnv1a, mulberry32, shuffleArray, getContestantDisplayOrder: order } = require('../../src/shuffleEngine');
const canonical = ['A', 'B', 'C', 'D'];
const q = Object.freeze({ id: 1, question_type: 'MCQ', options: Object.freeze({ A: 'Jake', B: 'Jane', C: 'John', D: 'Jill' }) });
const salt = 'OLFU_QUIZBEE_ITPM311';

test('FNV-1a matches known unsigned 32-bit vectors', () => {
  assert.equal(fnv1a(''), 2166136261);
  assert.equal(fnv1a('hello'), 0x4f9f2cab);
});
test('Mulberry32 has reproducible bounded output', () => {
  assert.equal(mulberry32(1)(), 0.6270739405881613);
  const a = mulberry32(42), b = mulberry32(42);
  for (let i = 0; i < 1000; i++) {
    const value = a();
    assert.equal(value, b());
    assert.ok(value >= 0 && value < 1);
  }
});
test('Fisher-Yates does not mutate its input', () => {
  assert.deepEqual(shuffleArray(Object.freeze([...canonical]), () => 0), ['B', 'C', 'D', 'A']);
  assert.deepEqual(shuffleArray([], mulberry32(1)), []);
});
test('1000 identical seeds yield identical positions; adjacent PIN fixtures differ', () => {
  const expected = order(q, 1001, salt);
  for (let i = 0; i < 1000; i++) assert.deepEqual(order(q, 1001, salt), expected);
  assert.equal(new Set([1001, 1002, 1003].map(id => order(q, id, salt).join(''))).size, 3);
});
test('every order preserves exactly four canonical labels and never changes option text', () => {
  for (let id = 1; id <= 60; id++) {
    for (let questionId = 1; questionId <= 20; questionId++) {
      assert.deepEqual(order({ ...q, id: questionId }, id, salt).sort(), canonical);
    }
  }
  assert.deepEqual(q.options, { A: 'Jake', B: 'Jane', C: 'John', D: 'Jill' });
});
test('identification, missing, malformed and fewer than two options bypass shuffling', () => {
  for (const question of [null, {}, { ...q, question_type: 'IDENTIFICATION' },
    ...[undefined, null, {}, [], 'bad json', { A: 'Jake' }].map(options => ({ ...q, options }))]) {
    assert.deepEqual(order(question, 1, salt), canonical);
  }
  assert.deepEqual(order({ ...q, options: JSON.stringify(q.options) }, 1, salt), order(q, 1, salt));
  assert.deepEqual(order({ ...q, options: { D: 'Jill', C: 'John', B: 'Jane', A: 'Jake' } }, 1, salt), order(q, 1, salt));
});
test('question, contestant and salt affect seed; results are independent arrays', () => {
  assert.notDeepEqual(order(q, 1, salt), order(q, 2, salt));
  assert.notDeepEqual(order(q, 1, salt), order({ ...q, id: 2 }, 1, salt));
  assert.ok(new Set(Array.from({ length: 20 }, (_, i) => order(q, 1, `salt-${i}`).join(''))).size > 1);
  const first = order(q, 1, salt); first.reverse();
  assert.notDeepEqual(first, order(q, 1, salt));
});
