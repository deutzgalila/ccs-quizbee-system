# Option shuffling

MCQ options are shuffled by default for authenticated contestants. The projector,
quizmaster and judges keep the canonical CSV/DB order. Identification questions
pass through unchanged.

- `ENABLE_OPTION_SHUFFLE=false` disables shuffling.
- `SHUFFLE_SEED_SALT` overrides the default `OLFU_QUIZBEE_ITPM311` salt.
- Keep the salt, shuffle configuration, question IDs/options and contestant IDs
  unchanged throughout a tournament, including server restarts. Changing them can
  change assignments and the interpretation of previously submitted letters.
- Embedded callers can pass `options.shuffleConfig`; `MODE: 'DISABLED'` also
  disables shuffling.

Assignments use FNV-1a, Mulberry32 and Fisher-Yates, seeded with
`question.id:contestant.id:salt`. They use the database contestant ID, not the
socket ID, so reconnection and reauthentication preserve assignments.

Contestants submit displayed letters. SQLite stores canonical letters, while
session restoration translates them back to the displayed buttons. Successful
shuffled-MCQ acknowledgments and pre-reveal session restoration withhold points
(`null`) and the current question's score contribution. At reveal, contestants
receive their displayed correct letter, answer text and updated total score.
Canonical mappings and seeds remain server-only.

There are only 24 permutations for four options. Independent deterministic
shuffles do not guarantee different assignments for every adjacent terminal;
even distinct permutations may place the correct answer at the same letter.
This reduces copying reliability but cannot eliminate it. A strict adjacent-seat
constraint would require a different assignment algorithm and seating model.

Verification: `npm test` passes 204 tests (188 baseline plus 16 new). Existing
SocketHandler unit fixtures explicitly disable shuffling because they submit
canonical letters; the new integration suite uses the enabled default with real
Socket.io clients and SQLite. The two T02 scoring scenarios run independently,
preserving the tournament's one-submission-per-question rule.
