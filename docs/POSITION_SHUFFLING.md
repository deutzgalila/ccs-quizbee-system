# Running label-preserving position shuffling

MCQ position shuffling is enabled by default. The same letter always identifies
the same option text on every screen. Contestants receive a deterministic
`display_order`; the existing buttons move using CSS Grid `order`. Projector,
quizmaster and judge states retain canonical order. Identification questions are
unchanged. Submission grading, stored answers and reveal letters remain canonical.

Configuration:

- `ENABLE_OPTION_SHUFFLE=false`: disable position shuffling.
- `SHUFFLE_SEED_SALT`: override the default `OLFU_QUIZBEE_ITPM311` salt.
- `SocketHandler` accepts `options.shuffleConfig` for embedded use. The enabled
  mode is `LABEL_PRESERVING_POSITION`.

Keep question IDs, contestant database IDs, the salt and configuration stable
during a tournament so reconnects and server restarts preserve positions.
The seed uses the contestant database ID, not its transient socket ID.

Four options have only 24 possible permutations. Independent deterministic
shuffles can collide, and a particular answer can occupy the same slot on two
terminals. This reduces blind quadrant copying but does not guarantee every
adjacent pair has different positions. Visible letters also remain shared.

The spatial-peeking integration fixture uses a fixed test salt to place A in
slot 3 for T01 and slot 2 for T02, with C in T02's slot 3. T02's correct attempt
runs independently from its copied attempt, preserving duplicate-submission
protection. Existing baseline tests run unchanged with shuffling enabled.

Each worktree uses its own default `quizbee.db`. Starting this branch does not
reuse the earlier option-shuffling worktree's terminal or question data. Select
an intentionally prepared database via `QUIZBEE_DB_PATH` when starting a server;
`npm run seed` is a destructive reset, not an additive provisioning command.
