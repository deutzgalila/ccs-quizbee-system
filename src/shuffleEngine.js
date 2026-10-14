/** Pure deterministic position shuffling. Letters always retain their option text. */
function fnv1a(str) {
  let hash = 2166136261;
  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function mulberry32(seed) {
  return function () {
    seed = (seed + 0x6D2B79F5) >>> 0;
    let t = seed;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffleArray(array, rng) {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

function getContestantDisplayOrder(question, contestantId, salt = '') {
  const keys = ['A', 'B', 'C', 'D'];
  if (question?.question_type !== 'MCQ') return keys;
  let options = question.options;
  if (typeof options === 'string') {
    try { options = JSON.parse(options); } catch (_) { return keys; }
  }
  if (!options || typeof options !== 'object' || Array.isArray(options) ||
      keys.filter(key => Object.hasOwn(options, key)).length < 2) return keys;
  return shuffleArray(keys, mulberry32(fnv1a(`${question.id}:${contestantId}:${salt}`)));
}

module.exports = { fnv1a, mulberry32, shuffleArray, getContestantDisplayOrder };
