/** Deterministic, server-only option mappings. Never serialize mappings to clients. */
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

function getContestantOptionMapping(question, contestantId, salt = '') {
  const options = question?.options;
  const keys = options && typeof options === 'object' && !Array.isArray(options)
    ? Object.keys(options).sort() : [];
  const displayedToCanonical = {};
  const canonicalToDisplayed = {};
  const shuffle = question?.question_type === 'MCQ' && keys.length >= 2;
  const order = shuffle
    ? shuffleArray(keys, mulberry32(fnv1a(`${question.id}:${contestantId}:${salt}`)))
    : keys;
  const shuffledOptions = shuffle ? {} : options;
  keys.forEach((displayed, i) => {
    const canonical = order[i];
    displayedToCanonical[displayed] = canonical;
    canonicalToDisplayed[canonical] = displayed;
    if (shuffle) shuffledOptions[displayed] = options[canonical];
  });
  const answer = question?.correct_answer;
  return {
    shuffledOptions, displayedToCanonical, canonicalToDisplayed,
    displayedCorrectAnswer: Object.hasOwn(canonicalToDisplayed, answer) ? canonicalToDisplayed[answer] : answer
  };
}

function toCanonicalAnswer(question, contestantId, answer, salt) {
  const { displayedToCanonical } = getContestantOptionMapping(question, contestantId, salt);
  return Object.hasOwn(displayedToCanonical, answer) ? displayedToCanonical[answer] : answer;
}

function toDisplayedAnswer(question, contestantId, answer, salt) {
  const { canonicalToDisplayed } = getContestantOptionMapping(question, contestantId, salt);
  return Object.hasOwn(canonicalToDisplayed, answer) ? canonicalToDisplayed[answer] : answer;
}

module.exports = { fnv1a, mulberry32, shuffleArray, getContestantOptionMapping, toCanonicalAnswer, toDisplayedAnswer };
