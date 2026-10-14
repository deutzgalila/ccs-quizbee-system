# Technical Specification: Answer Choice Randomization (Option Shuffling)

**Project**: Fatima QuizBee Engine (OLFU IT Olympics LAN Tournament — ITPM 311)  
**Target Agent**: Astra (Medium Effort / Medium Reasoning Tier)  
**Execution Environment**: Dedicated Git Worktree (`../quizbee-option-shuffling`)  
**Status**: Ready for Implementation  
**Baseline Test Suite**: 188 tests passing (100% green)  

---

## 1. Executive Summary & Problem Statement

### 1.1 Context
In the Our Lady of Fatima University (OLFU) IT Olympics Quiz Bee, up to 60 contestant workstations (`192.168.1.101`–`192.168.1.160`, PINs `1001`–`1060`) operate concurrently in a high-density university computer laboratory. Contestant terminals feature a prominent 2x2 grid representing Multiple Choice Question (MCQ) options (`A`, `B`, `C`, `D`).

### 1.2 The Vulnerability: Visual Peeking & Neighbor Mimicry
Because laboratory workstations are physically arranged in tight rows, contestants sitting side-by-side can easily observe an adjacent contestant's screen or hand movements. When option choices and their letter positions are identical across all monitors:
- A contestant who does not know the answer can glance at a neighbor's screen, see they clicked button "C" (bottom-left quadrant), and immediately click "C".
- In fast-paced 15-second Easy or 30-second Average rounds, this undermines tournament integrity and compromises the accuracy of scoring and tie-breaking.

### 1.3 The Solution: Server-Authoritative Deterministic Option Shuffling
We must introduce **Answer Choice Randomization (Option Shuffling)** for MCQ questions:
1. **Per-Contestant Randomization**: Every contestant terminal receives a unique, randomized permutation of the options (e.g., Contestant A sees option text under letter `B`, while Contestant B sees the same text under letter `D`).
2. **Deterministic & Drift-Proof**: The permutation is derived deterministically from the `(questionId, contestantId, salt)`. Browser refreshes, network drops, or socket reconnects mid-countdown return the *exact same* permutation without visual shifting or state corruption.
3. **Canonical Stage & Projector Preservation**: The Stage Projector (spectator display) and Quizmaster Dashboard retain the canonical option order (`A`, `B`, `C`, `D` as imported from CSV) so the Quizmaster can read options aloud naturally without confusing the live audience.
4. **Transparent Server Translation**: Contestants submit whichever letter is displayed on their screen (`A`, `B`, `C`, or `D`). The server translates the displayed letter to the canonical answer choice before scoring, logging, and persisting to SQLite.
5. **Zero Client Leakage**: Contestant clients NEVER receive canonical keys, shuffle seeds, or correct answer indicators prior to the official `REVEAL` phase.
6. **Zero Regression**: All 188 existing baseline tests must remain 100% passing.

---

## 2. Mandatory Git Worktree Protocol

To ensure clean isolation and prevent uncommitted collisions with the primary tree, **all implementation and testing must take place inside a new Git worktree**.

### 2.1 Worktree Setup Commands
From the repository root (`/home/kyle/quizbee-workspace/main`):

```bash
# 1. Ensure main working tree is clean
cd /home/kyle/quizbee-workspace/main
git status

# 2. Create the feature worktree on a new branch 'feature/option-shuffling'
git worktree add ../quizbee-option-shuffling -b feature/option-shuffling

# 3. Enter the new worktree
cd ../quizbee-option-shuffling

# 4. Link or verify node_modules
# (If node_modules is not already inherited/linked, create a symlink from main)
if [ ! -d "node_modules" ]; then
  ln -s /home/kyle/quizbee-workspace/main/node_modules ./node_modules
fi

# 5. Run baseline test suite to verify 100% green starting point
npm test
```

### 2.2 Worktree Execution Rules for Astra
- **Stay inside the worktree directory**: All edits, tests, and file creations must occur in `/home/kyle/quizbee-workspace/quizbee-option-shuffling`.
- **Do not modify files in `/home/kyle/quizbee-workspace/main`**.
- **Atomic Commits**: Commit modular milestones as they pass tests.

---

## 3. Architecture & Mathematical Specification

```
                                [CSV Question Bank / SQLite DB]
                               Canonical Options: { A: t1, B: t2, C: t3, D: t4 }
                               Canonical Correct Answer: 'C'
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     │                                                 │
            [Projector & Quizmaster]                          [Contestant Gateway]
          Canonical View Preserved                      _sanitizeGameStateForContestant()
          Option A: t1                                                 │
          Option B: t2                                 Deterministic Mulberry32 PRNG
          Option C: t3 (Correct)                       Seed: hash(q.id, contestant.id, salt)
          Option D: t4                                                 │
                                              ┌────────────────────────┴────────────────────────┐
                                              ▼                                                 ▼
                                     [Contestant T01]                                  [Contestant T02]
                            Permutation: ['B', 'D', 'A', 'C']                 Permutation: ['C', 'A', 'D', 'B']
                            A: t2                                             A: t3  <-- (Correct Answer)
                            B: t4                                             B: t1
                            C: t1                                             C: t4
                            D: t3  <-- (Correct Answer)                       D: t2
                                              │                                                 │
                                 Contestant submits: 'D'                           Contestant submits: 'A'
                                              │                                                 │
                                              └────────────────────────┬────────────────────────┘
                                                                       ▼
                                                       [Server: toCanonicalAnswer()]
                                                          T01: 'D' -> 'C' (Match!)
                                                          T02: 'A' -> 'C' (Match!)
                                                                       │
                                                       [SQLite SUBMISSIONS & Scoring]
                                                          Award 1pt, is_correct: 1
```

### 3.1 PRNG & Fisher-Yates Algorithm (`src/shuffleEngine.js`)

A pure, standalone utility module must be created with zero npm dependencies:

1. **32-Bit FNV-1a Hash**: Derives a deterministic integer seed from string keys.
   ```javascript
   function fnv1a(str) {
     let hash = 2166136261;
     for (let i = 0; i < str.length; i++) {
       hash ^= str.charCodeAt(i);
       hash = Math.imul(hash, 16777619);
     }
     return hash >>> 0;
   }
   ```

2. **Mulberry32 PRNG**: Generates pseudo-random floats in `[0, 1)` deterministically from a 32-bit state.
   ```javascript
   function mulberry32(seed) {
     return function() {
       let t = (seed += 0x6D2B79F5);
       t = Math.imul(t ^ (t >>> 15), t | 1);
       t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
       return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
     };
   }
   ```

3. **Fisher-Yates Shuffle**:
   ```javascript
   function shuffleArray(array, rng) {
     const arr = [...array];
     for (let i = arr.length - 1; i > 0; i--) {
       const j = Math.floor(rng() * (i + 1));
       [arr[i], arr[j]] = [arr[j], arr[i]];
     }
     return arr;
   }
   ```

4. **Contestant Option Mapping Contract**:
   Given a question object and a contestant ID (or PIN):
   - Canonical keys: `['A', 'B', 'C', 'D']`
   - Canonical options: `{ A: textA, B: textB, C: textC, D: textD }`
   - Shuffled keys: `shuffledOrder = shuffleArray(['A', 'B', 'C', 'D'], rng)`
   - Create mapping:
     - `displayedOptions`: An object `{ A: options[shuffledOrder[0]], B: options[shuffledOrder[1]], ... }`
     - `displayedToCanonical`: `{ A: shuffledOrder[0], B: shuffledOrder[1], ... }`
     - `canonicalToDisplayed`: `{ [shuffledOrder[0]]: 'A', [shuffledOrder[1]]: 'B', ... }`
     - `displayedCorrectAnswer`: `canonicalToDisplayed[canonicalCorrectAnswer]`

### 3.2 Key Invariants & Edge Cases
- **Non-MCQ Bypass**: Questions with `question_type !== 'MCQ'` (e.g., `IDENTIFICATION`) must immediately return unmodified state with no shuffling.
- **Malformed Options**: If a question has fewer than 2 options or is missing `options`, return unmodified state without throwing errors.
- **Reconnection Idempotency**: For a fixed `question.id`, `contestant.id`, and `salt`, `getContestantOptionMapping()` MUST return identical results across infinite invocations.
- **Fallback Resolution**: If a contestant submits an answer letter:
  1. First, check if `displayedToCanonical[answer]` exists.
  2. If not (or if shuffling is disabled), fallback to the raw answer.
  This ensures compatibility with direct tests and non-shuffled environments.

---

## 4. Configuration Specification (`src/config.js`)

Add a frozen configuration block `SHUFFLE_CONFIG` to `src/config.js`:

```javascript
const SHUFFLE_CONFIG = Object.freeze({
  ENABLED: process.env.ENABLE_OPTION_SHUFFLE !== 'false', // Default enabled; disable via env for legacy tests if needed
  MODE: 'PER_CONTESTANT', // 'PER_CONTESTANT' | 'DISABLED'
  SEED_SALT: process.env.SHUFFLE_SEED_SALT || 'OLFU_QUIZBEE_ITPM311'
});
```

Export `SHUFFLE_CONFIG` in `module.exports`.

---

## 5. Detailed Component Changes

### 5.1 New Module: `src/shuffleEngine.js`
Create `src/shuffleEngine.js` exporting:
- `fnv1a(str)`: string -> 32-bit uint.
- `mulberry32(seed)`: seed -> PRNG function.
- `shuffleArray(array, rng)`: deterministic in-place or copied array permutation.
- `getContestantOptionMapping(question, contestantId, salt)`: returns:
  ```javascript
  {
    shuffledOptions: { A: '...', B: '...', C: '...', D: '...' },
    displayedToCanonical: { A: 'C', B: 'A', C: 'D', D: 'B' },
    canonicalToDisplayed: { C: 'A', A: 'B', D: 'C', B: 'D' },
    displayedCorrectAnswer: 'A'
  }
  ```
- `toCanonicalAnswer(question, contestantId, displayedAnswer, salt)`: translates `'A'` -> `'C'`.
- `toDisplayedAnswer(question, contestantId, canonicalAnswer, salt)`: translates `'C'` -> `'A'`.

### 5.2 Server & Socket Gateway: `src/socketHandler.js`

1. **Import `shuffleEngine` and `SHUFFLE_CONFIG`**:
   Accept `options.shuffleConfig` in `SocketHandler` constructor (defaulting to `config.SHUFFLE_CONFIG`).

2. **Personalized State Sanitization**:
   Implement `_sanitizeGameStateForContestant(state, contestantId)`:
   - Clones sanitized state from `_sanitizeGameState(state)`.
   - If `state.currentQuestion` is MCQ and shuffling is enabled:
     - Calls `shuffleEngine.getContestantOptionMapping(state.currentQuestion, contestantId, salt)`.
     - Sets `sanitized.currentQuestion.options = mapping.shuffledOptions`.
     - Crucial: Never attach `displayedToCanonical`, `canonicalToDisplayed`, or `correct_answer` to this object!

3. **Phase Change Broadcasts**:
   In `engine.on('phase:change')`:
   - Keep Quizmaster and Judges unredacted (`room:quizmaster`, `room:judges`).
   - Emit CANONICAL sanitized state to `room:projector`:
     ```javascript
     const projectorState = this._sanitizeGameState(state);
     this.io.to('room:projector').emit('game:phase:change', {
       prevPhase,
       newPhase,
       autoExpired: !!autoExpired,
       state: projectorState
     });
     ```
   - Emit PERSONALIZED sanitized state to each contestant:
     Iterate active contestant sockets in `room:contestants`:
     ```javascript
     for (const [socketId, sock] of this.io.sockets.sockets) {
       if (sock.data?.role === 'CONTESTANT' && sock.data?.authenticated) {
         const contestantState = this._sanitizeGameStateForContestant(state, sock.data.contestantId || sock.data.pin);
         sock.emit('game:phase:change', {
           prevPhase,
           newPhase,
           autoExpired: !!autoExpired,
           state: contestantState
         });
       }
     }
     ```

4. **Contestant Join / Session Restore (`contestant:join`)**:
   When rehydrating state:
   - Use `this._sanitizeGameStateForContestant(engineState, contestant.id)` for `gameState`.
   - In `submissionStatus` / `session`:
     If contestant previously submitted, map canonical `priorSub.submitted_answer` back to `displayedAnswer` using `shuffleEngine.toDisplayedAnswer(...)` so the contestant's UI selects the exact button they clicked!

5. **Submission Handling (`contestant:submit`)**:
   - Receive `rawAnswer = String(payload.answer ?? '').trim()`.
   - If `qType === 'MCQ'` and shuffling is enabled:
     - Map to canonical: `const canonicalAnswer = shuffleEngine.toCanonicalAnswer(currentQ, contestant.id, rawAnswer, salt);`
     - Compare `canonicalAnswer` with `currentQ.correct_answer` to determine `isCorrect`.
   - Persist to SQLite:
     Store `canonicalAnswer` in `SUBMISSIONS.submitted_answer` (or store canonical while returning `rawAnswer` in acknowledgment), ensuring database queries and existing assertions like `assert.equal(sub.submitted_answer, 'C')` remain 100% compliant!
   - Acknowledgment: Return success and status to client.

6. **Answer Reveal Handling (`game:answer:reveal`)**:
   When transitioning to `REVEAL`:
   - Projector receives canonical correct answer:
     `this.io.to('room:projector').emit('game:answer:reveal', { questionId, correctAnswer: q.correct_answer, explanation: q.explanation });`
   - Each contestant receives their personalized displayed correct letter along with the canonical answer text:
     ```javascript
     for (const [socketId, sock] of this.io.sockets.sockets) {
       if (sock.data?.role === 'CONTESTANT' && sock.data?.authenticated) {
         const mapping = shuffleEngine.getContestantOptionMapping(state.currentQuestion, sock.data.contestantId || sock.data.pin, salt);
         sock.emit('game:answer:reveal', {
           questionId: state.currentQuestion.id,
           correctAnswer: mapping.displayedCorrectAnswer, // Button letter on THEIR screen!
           canonicalAnswer: state.currentQuestion.correct_answer,
           correctAnswerText: state.currentQuestion.options ? state.currentQuestion.options[state.currentQuestion.correct_answer] : '',
           explanation: state.currentQuestion.explanation || ''
         });
       }
     }
     ```

### 5.3 Client Script: `public/js/contestant.js`

1. **Option Rendering (`displayQuestion`)**:
   - `displayQuestion(q)` already populates `opts['A']`, `opts['B']`, `opts['C']`, `opts['D']`.
   - Because the server now sends personalized `options`, no radical DOM restructuring is required!

2. **Submission (`submitAnswer`)**:
   - Clicking button `A` continues to emit `{ questionId, answer: 'A' }`.

3. **Answer Reveal (`handleAnswerReveal`)**:
   - When `data.correctAnswer` arrives (which is the displayed letter for this terminal), the existing logic:
     `if (opt === correctUpper) btn.classList.add('is-correct');`
     will automatically highlight the CORRECT physical button on this contestant's screen!
   - Enhance the feedback message:
     If `data.correctAnswerText` is present:
     `showSubmissionStatus('✓ Correct! Answer: "' + data.correctAnswerText + '" (Option ' + data.correctAnswer + ') • +' + pts + ' PTS');`
     This gives clear, unambiguous validation to the student.

---

## 6. Testing & Quality Assurance Plan

Create a dedicated test file: `tests/unit/shuffleEngine.test.js` and an integration test file: `tests/integration/optionShuffling.test.js`.

### 6.1 Unit Tests (`tests/unit/shuffleEngine.test.js`)
1. **Determinism Test**: 1,000 runs of `getContestantOptionMapping(q, 1001)` produce the exact same permutation.
2. **Distinctness Across Terminals**: Terminal `1001`, `1002`, `1003` receive distinct option permutations for the same question.
3. **Bijection / Inversion Test**: `toCanonicalAnswer(toDisplayedAnswer(letter)) === letter` for all letters.
4. **Correct Answer Translation**: Verify that if canonical correct answer is `'C'`, `displayedOptions[displayedCorrectAnswer]` matches canonical `options['C']`.
5. **Non-MCQ Graceful Pass-through**: Identification questions return un-shuffled options without error.

### 6.2 Integration Tests (`tests/integration/optionShuffling.test.js`)
1. **Two-Contestant Peeking Simulation**:
   - Stage an MCQ question (`correct_answer: 'C'`).
   - Contestant 1 (PIN 1001) receives options where `'C'` is displayed at button `'A'`.
   - Contestant 2 (PIN 1002) receives options where `'C'` is displayed at button `'D'`.
   - Verify Contestant 1 and Contestant 2 received different option texts under button `'A'`.
   - Contestant 1 submits `'A'` -> Awarded 1 point.
   - Contestant 2 peeks, submits `'A'` (which is a wrong choice for T02!) -> Awarded 0 points.
   - Contestant 2 submits `'D'` -> Awarded 1 point.
2. **Reconnect & Refresh Consistency**:
   - Contestant disconnects mid-countdown, reconnects with same PIN.
   - Assert `gameState.currentQuestion.options` matches the pre-disconnect options exactly.
   - Assert `submissionStatus.submittedAnswer` re-selects the correct displayed button.
3. **Spectator Projector Isolation**:
   - Assert Projector socket receives canonical `{ A, B, C, D }` and NOT a shuffled permutation.
4. **Zero-Leakage Security Verification**:
   - Inspect the raw JSON payload emitted to Contestant socket.
   - Assert payload contains NO `canonicalAnswer`, `correct_answer`, `seed`, or `mapping` fields.

### 6.3 Regression Verification
Run the complete test suite:
```bash
npm test
```
**Acceptance Criterion**: All 188 existing baseline tests + all new shuffle tests must PASS with 0 failures, 0 errors.

---

## 7. Step-by-Step Task Delegation Checklist for Astra

| Step | Action | Files | Verification |
| :---: | :--- | :--- | :--- |
| **1** | Create and enter git worktree | `../quizbee-option-shuffling` | `git status`, `npm test` (188 pass) |
| **2** | Create `src/shuffleEngine.js` | `src/shuffleEngine.js` | Unit tests for PRNG and mappings |
| **3** | Add `tests/unit/shuffleEngine.test.js` | `tests/unit/shuffleEngine.test.js` | `node --test tests/unit/shuffleEngine.test.js` |
| **4** | Update configuration | `src/config.js` | `SHUFFLE_CONFIG` exported |
| **5** | Integrate into `SocketHandler` | `src/socketHandler.js` | Handle personalized emit, join restore, submit mapping, reveal emit |
| **6** | Update Contestant UI reveal text | `public/js/contestant.js` | Clear feedback on reveal |
| **7** | Add integration tests | `tests/integration/optionShuffling.test.js` | Multi-client peeking and reconnect tests pass |
| **8** | Run full regression suite | Complete codebase | `npm test` -> 100% pass |
| **9** | Commit changes to worktree branch | `git commit` | Clean git status on `feature/option-shuffling` |

---

## 8. Ready-to-Send Delegation Prompt for Astra

Copy and paste the prompt below when invoking Astra (Medium Effort):

```markdown
Hello Astra! You are assigned to implement **Answer Choice Randomization (Option Shuffling)** for the Fatima QuizBee Engine in this repository.

### Mission & Rules
1. **MANDATORY WORKTREE SETUP**:
   You must perform ALL your work in a dedicated git worktree, NEVER directly in `main`.
   Run the following commands from `/home/kyle/quizbee-workspace/main`:
   ```bash
   git worktree add ../quizbee-option-shuffling -b feature/option-shuffling
   cd ../quizbee-option-shuffling
   if [ ! -d "node_modules" ]; then
     ln -s /home/kyle/quizbee-workspace/main/node_modules ./node_modules
   fi
   npm test
   ```
   Verify that all 188 baseline tests pass before making any edits.

2. **SPECIFICATION REFERENCE**:
   Read and follow the full specification located at `docs/ANSWER_CHOICE_RANDOMIZATION_SPEC.md`.

3. **KEY DELIVERABLES**:
   - Create `src/shuffleEngine.js`: Deterministic FNV-1a + Mulberry32 PRNG + Fisher-Yates shuffle with bi-directional translation (`displayedToCanonical`, `canonicalToDisplayed`).
   - Create `tests/unit/shuffleEngine.test.js`: Comprehensive unit tests for determinism, distribution, and translations.
   - Update `src/config.js`: Add `SHUFFLE_CONFIG` with `ENABLED` and `MODE: 'PER_CONTESTANT'`.
   - Update `src/socketHandler.js`:
     - Personalize `game:phase:change` options for contestants; keep Projector canonical.
     - Translate displayed submission answer to canonical answer in `contestant:submit`.
     - Restore correct displayed letter on `contestant:join`.
     - Deliver personalized `correctAnswer` (displayed letter) and `correctAnswerText` on `game:answer:reveal`.
   - Update `public/js/contestant.js`: Polish reveal display feedback.
   - Create `tests/integration/optionShuffling.test.js`: Test peeking defense, reconnect consistency, and anti-leakage.
   - Maintain 100% backward compatibility: All 188 existing tests + new tests must pass (`npm test`).

4. **FINAL STEP**:
   Once all tests pass cleanly, commit your changes in the worktree branch `feature/option-shuffling`.
```
