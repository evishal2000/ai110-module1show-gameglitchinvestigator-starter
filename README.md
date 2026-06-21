# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

### Purpose

A Streamlit number-guessing game. The app picks a secret number within a range
that depends on the chosen difficulty (Easy `1–20`, Normal `1–100`, Hard `1–50`),
and the player guesses until they hit it or run out of attempts. After each guess
the game gives a higher/lower hint, tracks attempts and score, and exposes a
*Developer Debug Info* panel showing the live secret, attempts, score, and guess
history.

### Bugs Found

| #  | Bug | Symptom |
|----|-----|---------|
| 1  | Backwards hints | "Too High" told you to go higher (and vice-versa) |
| 2  | "New Game" dead | Button never reset `status`, so the game stayed stuck on the game-over screen |
| 3  | Attempts mistracked | Empty / `abc` input still consumed an attempt |
| 4  | Input not cleared | Guess box kept the previous value after submitting |
| 5  | Debug panel one submit behind | History/score reflected the *previous* guess, not the current one |
| 6  | Secret cast to string | Secret was stringified on even attempts, breaking numeric comparison |
| 7  | Difficulty missing from state | `st.session_state.difficulty` was never set, risking a `KeyError` |
| 8  | Hardcoded range prompt | Prompt always said "1 to 100" even on Easy/Hard |
| 9  | Difficulty-change mismatch | Changing difficulty mid-game left the secret outside the new range |

### Fixes Applied

- **Bug 1 & 6 (logic):** Centralized comparison in `check_guess` so `guess > secret`
  always maps to `"Too High"`, and always pass the real `int` secret — never a string.
- **Bug 2:** `start_new_round` now resets **every** piece of state including `status`,
  and "New Game" calls it, so a fresh round always starts.
- **Bug 3:** Validate input with `parse_guess` *before* incrementing attempts, so
  invalid input can't burn a turn.
- **Bug 4:** Clear the guess input box after each valid submit.
- **Bug 5:** Moved guess handling into an `on_click` callback that mutates state
  before the rerun, and render the debug panel after it — so it's always current.
- **Bug 7 & 9:** Store `difficulty` in session state and reset the round when it
  changes, keeping the secret inside the displayed range.
- **Bug 8:** Build the prompt from `get_range_for_difficulty` instead of literals.
- **Refactor & tests:** Moved the four core functions into `logic_utils.py`, added
  a root `conftest.py` to fix `ModuleNotFoundError`, and `pytest` passes green.

### Edge-Case Hardening

After the nine gameplay bugs were fixed, I probed `parse_guess` for inputs that
were still mishandled and hardened all three (now covered by `pytest`):

| Edge case | Old behavior | New behavior |
|-----------|--------------|--------------|
| `inf` / `1e999` / `nan` | `int(float("inf"))` raised `OverflowError`, which the `except ValueError` **didn't** catch → app crash | Routed through `float()` and rejected via `math.isinf`/`math.isnan` as `"That is not a number."` |
| Out-of-range numbers (`-50`, `999999`) | Accepted as real guesses — burned an attempt and docked score despite being outside the displayed range | `parse_guess(raw, low, high)` rejects them *before* an attempt is counted |
| Fractional decimals (`42.9`) | Silently truncated to `42`, so a "wrong" number could win | Rejected as `"Enter a whole number."`; whole-valued decimals like `42.0` still accepted |

The suite now has **39 passing tests** (up from 14), including parametrized cases
for each edge case above.

#### Test Run Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.0.3, pluggy-1.6.0 -- /Users/vishalelaka/Documents/Github/ai110-module1show-gameglitchinvestigator-starter/venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/vishalelaka/Documents/Github/ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.13.0
collecting ... collected 39 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  2%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  5%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [  7%]
tests/test_game_logic.py::test_high_guess_is_never_too_low PASSED        [ 10%]
tests/test_game_logic.py::test_low_guess_is_never_too_high PASSED        [ 12%]
tests/test_game_logic.py::test_check_guess_is_numeric_not_string_compare PASSED [ 15%]
tests/test_game_logic.py::test_parse_guess_rejects_empty PASSED          [ 17%]
tests/test_game_logic.py::test_parse_guess_rejects_whitespace PASSED     [ 20%]
tests/test_game_logic.py::test_parse_guess_rejects_non_number PASSED     [ 23%]
tests/test_game_logic.py::test_parse_guess_accepts_valid_int PASSED      [ 25%]
tests/test_game_logic.py::test_range_easy PASSED                         [ 28%]
tests/test_game_logic.py::test_range_normal PASSED                       [ 30%]
tests/test_game_logic.py::test_range_hard PASSED                         [ 33%]
tests/test_game_logic.py::test_wrong_guess_loses_points PASSED           [ 35%]
tests/test_game_logic.py::test_parse_guess_rejects_inf_and_nan[inf] PASSED [ 38%]
tests/test_game_logic.py::test_parse_guess_rejects_inf_and_nan[Inf] PASSED [ 41%]
tests/test_game_logic.py::test_parse_guess_rejects_inf_and_nan[-inf] PASSED [ 43%]
tests/test_game_logic.py::test_parse_guess_rejects_inf_and_nan[infinity] PASSED [ 46%]
tests/test_game_logic.py::test_parse_guess_rejects_inf_and_nan[1e999] PASSED [ 48%]
tests/test_game_logic.py::test_parse_guess_rejects_inf_and_nan[1E999] PASSED [ 51%]
tests/test_game_logic.py::test_parse_guess_rejects_inf_and_nan[nan] PASSED [ 53%]
tests/test_game_logic.py::test_parse_guess_rejects_inf_and_nan[NaN] PASSED [ 56%]
tests/test_game_logic.py::test_parse_guess_does_not_raise_on_infinity PASSED [ 58%]
tests/test_game_logic.py::test_parse_guess_accepts_plain_scientific_notation PASSED [ 61%]
tests/test_game_logic.py::test_parse_guess_rejects_out_of_range[-50] PASSED [ 64%]
tests/test_game_logic.py::test_parse_guess_rejects_out_of_range[0] PASSED [ 66%]
tests/test_game_logic.py::test_parse_guess_rejects_out_of_range[21] PASSED [ 69%]
tests/test_game_logic.py::test_parse_guess_rejects_out_of_range[999999] PASSED [ 71%]
tests/test_game_logic.py::test_parse_guess_accepts_in_range_boundaries[1-1] PASSED [ 74%]
tests/test_game_logic.py::test_parse_guess_accepts_in_range_boundaries[20-20] PASSED [ 76%]
tests/test_game_logic.py::test_parse_guess_accepts_in_range_boundaries[13-13] PASSED [ 79%]
tests/test_game_logic.py::test_parse_guess_without_range_still_accepts_large_int PASSED [ 82%]
tests/test_game_logic.py::test_parse_guess_rejects_fractional_decimals[42.9] PASSED [ 84%]
tests/test_game_logic.py::test_parse_guess_rejects_fractional_decimals[-0.5] PASSED [ 87%]
tests/test_game_logic.py::test_parse_guess_rejects_fractional_decimals[19.99] PASSED [ 89%]
tests/test_game_logic.py::test_parse_guess_rejects_fractional_decimals[0.1] PASSED [ 92%]
tests/test_game_logic.py::test_parse_guess_accepts_whole_valued_decimals[42.0-42] PASSED [ 94%]
tests/test_game_logic.py::test_parse_guess_accepts_whole_valued_decimals[7.000-7] PASSED [ 97%]
tests/test_game_logic.py::test_fractional_decimal_is_rejected_even_when_in_range PASSED [100%]

============================== 39 passed in 0.02s ==============================
```

See [reflection.md](reflection.md) for the full debugging write-up.

## 📸 Demo Walkthrough

A sample game on **Normal** difficulty (range **1–100**, 8 attempts). Assume the
secret number shown in *Developer Debug Info* is **55**.

1. User enters a guess of **40** and clicks **Submit Guess 🚀**.
2. Game returns **"📈 Go HIGHER!"** (`check_guess` → `"Too Low"`); attempts = 1, score = **−5**.
3. User enters a guess of **70** → **"📉 Go LOWER!"** (`"Too High"`); attempts = 2, score = **−10**.
4. The debug panel and score update **on the same submit** — no longer one guess behind.
5. User enters **55** → **"🎉 Correct!"**; the win adds `100 − 10 × (3 − 1) = 80` points, so the final score = **70**.
6. Game ends: a success banner reads *"You won! The secret was 55. Final score: 70"*, **Submit** is disabled, and **New Game 🔁** starts a fresh round.

## 🚀 Stretch Features

### 🏆 Persistent High Score Tracker

The game now tracks the **best winning score per difficulty** and saves it to
`high_scores.json`, so your records survive app restarts.

- **Where it lives:** the pure logic is in `logic_utils.py` —
  `update_high_scores` (decides if a score is a new record), `load_high_scores`
  (reads the file, gracefully returning `{}` on a missing/corrupt/non-dict file),
  and `save_high_scores` (writes JSON).
- **In the app:** a **🏆 High Scores** panel in the sidebar shows the best score
  for Easy / Normal / Hard (with `⬅` marking the current difficulty). Beating your
  best on a win triggers balloons and a "New high score!" banner, and the new
  record is persisted immediately.
- **Why a win only:** scores are only banked on a win (a loss only ever loses
  points), and a tie doesn't count — you must *strictly* beat the previous best.
- **Robustness:** loading is fault-tolerant by design (missing file, bad JSON,
  wrong shape, or non-integer values all degrade to a clean slate rather than a
  crash), and the runtime `high_scores.json` is git-ignored.
- **Tests:** 11 new cases cover the record/tie/lower logic, per-difficulty
  tracking, input-dict immutability, and the save→load round trip plus every
  graceful-failure path. The suite is now **50 passing tests**.

### 🔥 Friendlier Output: Hot/Cold Hints & Session Summary

Layered structured, user-friendly feedback on top of the existing game —
**without touching the win/lose or scoring logic**. The win/lose decision still
comes only from `check_guess`, and the score only from `update_score`.

#### What was added / modified

| Function / section | File | What it now outputs |
|--------------------|------|---------------------|
| `proximity_label(guess, secret, low, high)` (new, pure) | [logic_utils.py:188](logic_utils.py#L188) | A `(state, emoji)` pair describing closeness — `("Bullseye", "🎯")`, `("Hot", "🔥")`, `("Warm", "♨️")`, `("Cool", "🌤️")`, or `("Cold", "🧊")`. |
| `start_new_round(difficulty)` (modified) | [app.py:33](app.py#L33) | Now also initializes `st.session_state.guess_log = []` so the summary resets each round. |
| `handle_submit(difficulty)` (modified) | [app.py:54](app.py#L54) | Calls `proximity_label` ([app.py:88](app.py#L88)), appends a structured row to `guess_log` ([app.py:93](app.py#L93)), and enriches the hint feedback ([app.py:115](app.py#L115)). |
| Session Summary render block (new) | [app.py:236](app.py#L236) | Renders metrics + an `st.table(guess_log)`. |

#### How it behaves

- **Hot/Cold proximity** — `proximity_label` judges distance *as a fraction of
  the range*, so "Hot" means the same closeness on Easy (1–20) as on Normal
  (1–100). For example, `proximity_label(52, 50, 1, 100)` → `("Hot", "🔥")`.
- **Enriched hints** — `handle_submit` pairs the directional hint with the
  proximity, so the amber hint banner now reads e.g. **"📈 Go HIGHER!  ·  🔥 Hot"**
  instead of just the direction.
- **Color-coded feedback** — wins render green (`st.success`), hints amber
  (`st.warning`), and errors/game-over red (`st.error`).
- **📋 Session Summary table** — each guess appends a row
  `{"#", "Guess", "Result", "Proximity", "Score"}` to `guess_log`; the render
  block shows three `st.metric` tiles (total guesses, current score, closest
  guess) above an `st.table` of every row.
- **Safety** — proximity is purely cosmetic and guards against a zero-width
  range (no `ZeroDivisionError`); `guess_log` is separate from the existing
  `history`/debug panel, so nothing in the core flow changed.
- **Tests** — 9 new cases pin the bands, range-relative scaling, exact-match
  Bullseye, and the degenerate-range guard. The suite is now **59 passing
  tests**.

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
