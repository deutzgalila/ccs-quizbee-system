# Technical Specification: Label-Preserving Position Shuffling (Visual Grid Scrambling)

**Project**: Fatima QuizBee Engine (OLFU IT Olympics LAN Tournament — ITPM 311)  
**Feature Name**: Label-Preserving Position Shuffling (Spatial Grid / Visual Layout Randomization)  
**Target Agent**: Astra (Medium Effort / Medium Reasoning Tier)  
**Execution Environment**: Dedicated Git Worktree (`../quizbee-position-shuffling`)  
**Status**: Ready for Implementation  
**Baseline Test Suite**: 188 baseline tests passing  

---

## 1. Executive Summary & Paradigm Review

### 1.1 The Requirement
In a live stage Quiz Bee, the host/Quizmaster speaks over a microphone and the audience watches a central 1080p projector.
- The Projector and Quizmaster announce options in canonical order:
  - **A.** Jake
  - **B.** Jane
  - **C.** John
  - **D.** Jill
- On the Contestant Terminals (T01–T60), the options must retain their canonical letter bindings (`A` is always Jake, `B` is always Jane, `C` is always John, `D` is always Jill), but the **spatial/visual positions (slots) of the buttons are shuffled per contestant**:
  - **Contestant T01 Screen**:
    `[ B. Jane ]` `[ C. John ]` `[ A. Jake ]` `[ D. Jill ]`
  - **Contestant T02 Screen**:
    `[ D. Jill ]` `[ A. Jake ]` `[ B. Jane ]` `[ C. John ]`

### 1.2 Comparison: Label-Preserving Shuffling vs Letter Reassignment

| Dimension | Type 1: Letter Reassignment | **Type 2: Label-Preserving Position Shuffling (THIS SPEC)** |
| :--- | :--- | :--- |
| **Option Letter Binding** | Letter shifts: `A` becomes Jane for T01, `C` for T02. | **Letter stays bound to content**: `A` is ALWAYS Jake, `B` is ALWAYS Jane. |
| **Visual Button Position** | Fixed slots 1, 2, 3, 4 always show `A`, `B`, `C`, `D`. | **Shuffled slots**: Buttons physically move to different grid cells. |
| **Auditory & Stage Sync** | Host saying *"The answer is A: Jake"* conflicts with contestants who have Jake under `B` or `C`. | **100% Unified**: Host, Projector, and Contestants all agree that Jake is `A`. |
| **Anti-Peeking Mechanism** | Foils letter peeking, but buttons stay in place. | **Foils spatial/quadrant peeking**: A neighbor blind-copying slot 3 clicks Jake on T01, but Jane on T02! |
| **Server Translation Complexity** | Requires bi-directional translation tables and risk of submission desync. | **Zero translation layer**: Clicking `A` submits `A` and grades against canonical `A`. |
| **Backward Compatibility** | Requires test accommodation. | **100% native compatibility** with all existing test suites. |

---

## 2. Mandatory Git Worktree Protocol

All development, testing, and commits must take place inside a dedicated git worktree to maintain clean isolation from `main`.

### 2.1 Worktree Setup Commands
From the repository root (`/home/kyle/quizbee-workspace/main`):

```bash
# 1. Ensure main working tree is clean
cd /home/kyle/quizbee-workspace/main
git status

# 2. Create the feature worktree on a new branch 'feature/label-preserving-shuffling'
git worktree add ../quizbee-position-shuffling -b feature/label-preserving-shuffling

# 3. Switch into the worktree
cd ../quizbee-position-shuffling

# 4. Link node_modules
if [ ! -d "node_modules" ]; then
  ln -s /home/kyle/quizbee-workspace/main/node_modules ./node_modules
fi

# 5. Verify the baseline test suite passes
npm test
```

---

## 3. Architecture & Mechanics

```
                             [SQLite / CSV Question Bank]
                         Canonical Options: { A: 'Jake', B: 'Jane', C: 'John', D: 'Jill' }
                         Correct Answer: 'A'
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            │                                                     │
   [Projector & Quizmaster]                              [Contestant Gateway]
  Canonical display_order:                             Deterministic Mulberry32 PRNG
  ['A', 'B', 'C', 'D']                                 Seed: hash(q.id, contestant.id, salt)
            │                                                     │
            ▼                                         ┌───────────┴───────────┐
     [Stage Screen]                                   ▼                       ▼
  Slot 1: [ A. Jake ]                         [Contestant T01]        [Contestant T02]
  Slot 2: [ B. Jane ]                         display_order:          display_order:
  Slot 3: [ C. John ]                         ['B', 'C', 'A', 'D']    ['D', 'A', 'B', 'C']
  Slot 4: [ D. Jill ]                                 │                       │
                                                      ▼                       ▼
                                              Slot 1: [ B. Jane ]     Slot 1: [ D. Jill ]
                                              Slot 2: [ C. John ]     Slot 2: [ A. Jake ]
                                              Slot 3: [ A. Jake ]     Slot 3: [ B. Jane ]
                                              Slot 4: [ D. Jill ]     Slot 4: [ C. John ]
                                                      │                       │
                                              Clicks: Button 'A'      Clicks: Button 'A'
                                              Submits: { answer: 'A' } Submits: { answer: 'A' }
                                                      │                       │
                                                      └───────────┬───────────┘
                                                                  ▼
                                                   [Server: Direct Evaluation]
                                                      'A' === 'A' -> CORRECT!
                                                      Persist 'A' to SUBMISSIONS
```

### 3.1 Deterministic Order Derivation (`src/shuffleEngine.js`)

The order of buttons is derived deterministically from `(questionId, contestantId, salt)`:
1. **Canonical Keys**: `['A', 'B', 'C', 'D']`.
2. **Deterministic Seed**: `fnv1a(`${question.id}:${contestantId}:${salt}`)`.
3. **Seeded Fisher-Yates**: Permutes the array of keys:
   - For T01: `display_order = ['B', 'C', 'A', 'D']`.
   - For T02: `display_order = ['D', 'A', 'B', 'C']`.
4. **Non-MCQ Pass-through**: For `IDENTIFICATION` questions, `display_order` is `null` or `['A', 'B', 'C', 'D']`.

### 3.2 Visual Grid Ordering via CSS `order`

In `public/contestant.html`, the MCQ buttons are inside `.mcq-grid`:
```html
<div id="mcq-container" class="mcq-grid">
  <button id="opt-a" class="mcq-option-btn" data-option="A">
    <span class="mcq-letter">A</span>
    <span class="mcq-text" id="text-opt-a">Jake</span>
  </button>
  <button id="opt-b" class="mcq-option-btn" data-option="B">
    <span class="mcq-letter">B</span>
    <span class="mcq-text" id="text-opt-b">Jane</span>
  </button>
  <button id="opt-c" class="mcq-option-btn" data-option="C">
    <span class="mcq-letter">C</span>
    <span class="mcq-text" id="text-opt-c">John</span>
  </button>
  <button id="opt-d" class="mcq-option-btn" data-option="D">
    <span class="mcq-letter">D</span>
    <span class="mcq-text" id="text-opt-d">Jill</span>
  </button>
</div>
```

Because `.mcq-grid` uses `display: grid`:
CSS standard specifies that grid items are placed in order of their **CSS `order`** property!
When `display_order = ['B', 'C', 'A', 'D']`:
- Button `B`: `style.order = 1` -> Renders in Slot 1 (top-left)
- Button `C`: `style.order = 2` -> Renders in Slot 2 (top-right)
- Button `A`: `style.order = 3` -> Renders in Slot 3 (bottom-left)
- Button `D`: `style.order = 4` -> Renders in Slot 4 (bottom-right)

**Key Advantages**:
- Button `A` still has `id="opt-a"` and `data-option="A"`.
- Button `A` still contains letter badge `A` and text `Jake`.
- Clicking button `A` naturally submits `answer: 'A'`.
- On reveal, adding `.is-correct` to `#opt-a` highlights button `A` in green right where it sits in Slot 3!
- Zero DOM element destruction, zero listener re-binding, zero risk of memory leaks.

---

## 4. Component Implementation Plan

### 4.1 `src/shuffleEngine.js`
Exports:
- `fnv1a(str)`: 32-bit hash function.
- `mulberry32(seed)`: Seeded PRNG.
- `shuffleArray(arr, rng)`: Fisher-Yates array permutation.
- `getContestantDisplayOrder(question, contestantId, salt)`:
  - If `question.question_type !== 'MCQ'`, returns `['A', 'B', 'C', 'D']`.
  - For MCQ, returns deterministic shuffled array of keys, e.g. `['B', 'C', 'A', 'D']`.

### 4.2 `src/config.js`
Ensure `SHUFFLE_CONFIG` is configured:
```javascript
const SHUFFLE_CONFIG = Object.freeze({
  ENABLED: process.env.ENABLE_OPTION_SHUFFLE !== 'false',
  MODE: 'LABEL_PRESERVING_POSITION', // Visual position shuffling
  SEED_SALT: process.env.SHUFFLE_SEED_SALT || 'OLFU_QUIZBEE_ITPM311'
});
```

### 4.3 `src/socketHandler.js`
1. **Personalized State for Contestants**:
   In `_sanitizeGameStateForContestant(state, contestantId)`:
   - Sets `sanitized.currentQuestion.options` = canonical options `{ A: 'Jake', B: 'Jane', ... }`.
   - Attaches `sanitized.currentQuestion.display_order` = `shuffleEngine.getContestantDisplayOrder(question, contestantId, salt)`.
2. **Projector & Quizmaster**:
   - `_sanitizeGameState(state)` leaves `display_order = ['A', 'B', 'C', 'D']` (canonical order).
3. **Submissions (`contestant:submit`)**:
   - The contestant submits `answer: 'A'`.
   - Because `A` is canonical, **no translation is needed**! Direct comparison:
     `isCorrect = rawAnswer.toUpperCase() === currentQ.correct_answer.toUpperCase()`.
   - Persist `rawAnswer` directly to SQLite `SUBMISSIONS.submitted_answer`.
4. **Answer Reveal (`game:answer:reveal`)**:
   - `correctAnswer: currentQ.correct_answer` is universally broadcast to all clients.
   - Every client highlights the button with `data-option === correctAnswer`. Since the button is positioned via CSS `order`, it lights up in its scrambled slot accurately!

### 4.4 `public/js/contestant.js`
In `displayQuestion(q)`:
```javascript
const displayOrder = q.display_order || ['A', 'B', 'C', 'D'];
['A', 'B', 'C', 'D'].forEach((letter) => {
  const btn = document.getElementById(`opt-${letter.toLowerCase()}`);
  if (btn) {
    const slotIndex = displayOrder.indexOf(letter);
    btn.style.order = slotIndex !== -1 ? (slotIndex + 1) : 0;
  }
});
```
On `handleAnswerReveal(data)`:
The existing code already checks:
```javascript
mcqOptionButtons.forEach((btn) => {
  const opt = (btn.dataset.option || '').toUpperCase();
  if (opt === correctUpper) {
    btn.classList.add('is-correct');
  }
});
```
Because the button with `data-option="A"` has `style.order = 3`, it highlights green in Slot 3 automatically!

---

## 5. Verification & Test Suite

### 5.1 Unit Tests (`tests/unit/shuffleEngine.test.js`)
- **Determinism**: 1,000 invocations of `getContestantDisplayOrder(q, 1001)` return the exact same array.
- **Neighbor Distinctness**: Verify adjacent terminals (e.g. 1001, 1002, 1003) produce distinct visual slot sequences for question 1.
- **Element Completeness**: Shuffled array always contains exactly `['A', 'B', 'C', 'D']` with no duplicates or dropped keys.
- **Pass-through**: Identification questions return `['A', 'B', 'C', 'D']`.

### 5.2 Integration Tests (`tests/integration/positionShuffling.test.js`)
1. **Peeking Defense Simulation**:
   - Question 1 has `correct_answer: 'A'` ("Jake").
   - Contestant 1 (PIN 1001) receives `display_order` where `'A'` is in Slot 3 (bottom-left).
   - Contestant 2 (PIN 1002) receives `display_order` where `'A'` is in Slot 2 (top-right), and Slot 3 holds `'C'`.
   - Contestant 1 clicks button `A` (in Slot 3) -> Submits `A` -> **1 point awarded**.
   - Contestant 2 peeks at Contestant 1 clicking Slot 3 and clicks Slot 3 on their own screen (Button `C`) -> Submits `C` -> **0 points awarded**!
   - Contestant 2 clicks button `A` (in Slot 2) -> Submits `A` -> **1 point awarded**.
2. **Reconnection Stability**:
   - Contestant reconnects mid-countdown.
   - Assert `gameState.currentQuestion.display_order` is identical to pre-disconnect state.
3. **Projector Canonical Order**:
   - Projector receives `display_order: ['A', 'B', 'C', 'D']`.

### 5.3 Regression Guarantee
Run `npm test`:
- All 188 baseline tests + all new tests pass with 0 failures.

---

## 6. Ready-to-Send Delegation Prompt for Astra

```markdown
Hello Astra! You are assigned to implement **Label-Preserving Position Shuffling (Visual Grid Scrambling)** for the Fatima QuizBee Engine.

### 1. Mandatory Git Worktree Setup
Perform all work inside a dedicated git worktree from `/home/kyle/quizbee-workspace/main`:
```bash
git worktree add ../quizbee-position-shuffling -b feature/label-preserving-shuffling
cd ../quizbee-position-shuffling
if [ ! -d "node_modules" ]; then
  ln -s /home/kyle/quizbee-workspace/main/node_modules ./node_modules
fi
npm test
```

### 2. Specification Document
Read and follow: `docs/LABEL_PRESERVING_POSITION_SHUFFLING_SPEC.md`

### 3. Key Deliverables
1. **`src/shuffleEngine.js`**:
   - Implement `fnv1a`, `mulberry32`, `shuffleArray`.
   - Implement `getContestantDisplayOrder(question, contestantId, salt)`.
2. **`tests/unit/shuffleEngine.test.js`**:
   - Unit tests for determinism, distribution, and key completeness.
3. **`src/socketHandler.js`**:
   - In `_sanitizeGameStateForContestant()`, attach `display_order` for MCQ questions.
   - Submissions evaluate directly (no letter translation tables needed).
   - Projector receives canonical order `['A', 'B', 'C', 'D']`.
4. **`public/js/contestant.js`**:
   - In `displayQuestion(q)`, apply `btn.style.order = display_order.indexOf(letter) + 1` to `#opt-a`, `#opt-b`, `#opt-c`, `#opt-d`.
5. **`tests/integration/positionShuffling.test.js`**:
   - Test spatial peeking defense (neighbor clicking the wrong button by copying physical slot), reconnect consistency, and projector canonical order.
6. **Regression**:
   - Run `npm test` and ensure 100% pass rate.
   - Commit cleanly to `feature/label-preserving-shuffling`.
```
