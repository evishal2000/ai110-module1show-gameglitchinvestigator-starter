# 🤖 AI Interactions — Edge-Case Test Generation

A log of the prompts I gave Claude (Claude Code, agent mode) to generate the
edge-case test suite for `parse_guess`, plus why each edge case was chosen.

## Prompts Used

1. **Identify the edge cases:**

   > identify three potential "edge case" inputs (e.g., negative numbers, decimals, or extremely large values) that might still break

2. **Generate the tests:**
   > generate a suite of pytest cases that verify the game handles these inputs gracefully.

These produced the new tests in [tests/test_game_logic.py](tests/test_game_logic.py)
and the supporting hardening of `parse_guess` in [logic_utils.py](logic_utils.py).

## Edge Cases Chosen — and Why

| #   | Edge case                              | One-line reason it was chosen                                                                                                           |
| --- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `inf` / `1e999` / `nan`                | `int(float("inf"))` raises `OverflowError`, which the old `except ValueError` didn't catch — a real crash, not just a bad guess.        |
| 2   | Out-of-range numbers (`-50`, `999999`) | The parser checked "is it a number?" but never "is it in range?", so a negative or huge value counted as a real guess and docked score. |
| 3   | Fractional decimals (`42.9`)           | `int(float("42.9"))` silently truncated to `42`, so a "wrong" number could win — a misleading-input bug rather than a crash.            |

## Agent Workflow

A chronological log of what I asked Claude (Claude Code, agent mode) to do across
this session, the files it touched, and what it completed.

### Step 1 — Identify edge cases

- **Asked:** Identify three edge-case inputs that could still break the game.
- **Files modified:** none (analysis only).
- **Completed:** Found three — `inf`/`1e999`/`nan` (uncaught `OverflowError`),
  out-of-range numbers, and truncated fractional decimals — read against
  `logic_utils.py` and `app.py`.

### Step 2 — Generate edge-case tests (+ hardening)

- **Asked:** Generate a pytest suite that verifies the game handles those inputs
  gracefully.
- **Files modified:** `logic_utils.py` (hardened `parse_guess`: route through
  `float()`, reject inf/nan via `math`, reject fractions, optional `low`/`high`
  range check), `app.py` (pass the difficulty range into `parse_guess`),
  `tests/test_game_logic.py` (added the edge-case cases).
- **Completed:** 25 new tests added; suite grew from 14 → 39, all passing.

### Step 3 — Document the hardening

- **Asked:** Update the README and reflection to mention the hardening.
- **Files modified:** `README.md` (Edge-Case Hardening section + before/after
  table), `reflection.md` (Q3 bullet on the three edge cases).
- **Completed:** Both docs updated; test count noted as 39.

### Step 4 — Paste the test output

- **Asked:** Paste the terminal output showing all tests passing into the README
  as a fenced code block (not a screenshot).
- **Files modified:** `README.md` (added a "Test Run Output" fenced block).
- **Completed:** Full `pytest -v` output (39 passed) embedded as a `text` block.

### Step 5 — Record the AI interactions

- **Asked:** Record the prompts used to generate the tests and a one-line reason
  for each edge case.
- **Files modified:** `ai_interactions.md` (created).
- **Completed:** Prompts and the edge-case rationale table written.

### Step 6 — Plan & implement a new feature (High Score tracker)

- **Asked:** Plan and implement a meaningful new feature (e.g. a persistent High
  Score tracker).
- **Files modified:** `logic_utils.py` (`update_high_scores`, `load_high_scores`,
  `save_high_scores`), `app.py` (load-once on session start, bank-on-win + save,
  🏆 sidebar panel, new-record banner/balloons), `tests/test_game_logic.py`
  (11 new tests), `.gitignore` (ignore runtime `high_scores.json`), `README.md`
  (Stretch Features write-up).
- **Completed:** Feature implemented; suite grew 39 → 50, all passing; app boots
  headless under Streamlit with no errors.

### Step 7 — Document the agent workflow

- **Asked:** Add this "Agent Workflow" section.
- **Files modified:** `ai_interactions.md` (this section).
- **Completed:** Per-step log of asks, files touched, and outcomes.

### Files Modified (session total)

| File | What changed |
|------|--------------|
| `logic_utils.py` | Hardened `parse_guess`; added the High Score functions |
| `app.py` | Range-checked parsing; wired the High Score tracker + sidebar/banner |
| `tests/test_game_logic.py` | +36 tests (edge cases + high score); 14 → 50 total |
| `README.md` | Edge-Case Hardening section, pasted test output, High Score feature |
| `reflection.md` | Edge-case hardening bullet under Q3 |
| `.gitignore` | Ignore runtime `high_scores.json` |
| `ai_interactions.md` | Prompts, edge-case rationale, and this Agent Workflow log |

## PEP 8 Linting Pass

### Prompts Used

1. **Add docstrings:**
   > add professional-grade docstrings to every function in logic_utils.py

2. **Lint for PEP 8:**
   > review the code for PEP 8 style compliance and resolve any formatting or naming issues

### Tools

`pycodestyle` (PEP 8 formatting) and `pyflakes` (unused imports / undefined
names) were installed into the git-ignored `venv` and run at the default
line-length of 79.

### Linting Output — Before

```text
app.py:34:80: E501 line too long (81 > 79 characters)
app.py:35:80: E501 line too long (80 > 79 characters)
app.py:134:80: E501 line too long (80 > 79 characters)
logic_utils.py:14:80: E501 line too long (80 > 79 characters)
logic_utils.py:17:1: E302 expected 2 blank lines, found 1
logic_utils.py:109:80: E501 line too long (84 > 79 characters)
logic_utils.py:183:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:15:1: E302 expected 2 blank lines, found 1
tests/test_game_logic.py:20:1: E302 expected 2 blank lines, found 1
tests/test_game_logic.py:25:1: E302 expected 2 blank lines, found 1
tests/test_game_logic.py:31:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:38:1: E302 expected 2 blank lines, found 1
tests/test_game_logic.py:42:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:47:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:51:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:57:1: E302 expected 2 blank lines, found 1
tests/test_game_logic.py:61:1: E302 expected 2 blank lines, found 1
tests/test_game_logic.py:65:1: E302 expected 2 blank lines, found 1
tests/test_game_logic.py:70:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:75:1: E302 expected 2 blank lines, found 1
tests/test_game_logic.py:78:1: E302 expected 2 blank lines, found 1
tests/test_game_logic.py:82:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:89:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:91:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:92:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:96:80: E501 line too long (99 > 79 characters)
tests/test_game_logic.py:105:80: E501 line too long (81 > 79 characters)
tests/test_game_logic.py:118:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:142:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:168:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:233:80: E501 line too long (93 > 79 characters)
conftest.py:2:80: E501 line too long (81 > 79 characters)
# pyflakes: (no output — 0 issues)
```

### Linting Output — After

```text
$ pycodestyle app.py logic_utils.py tests/test_game_logic.py conftest.py
(no output — 0 issues)

$ pyflakes app.py logic_utils.py tests/test_game_logic.py conftest.py
(no output — 0 issues)
```

### What the AI Suggested vs. Applied

| Suggested change | Applied? | Notes |
|------------------|----------|-------|
| **E302** — add a 2nd blank line before top-level `def`s (9 spots) | ✅ Applied | Pure spacing; includes the original 3 tests that used single blank lines. |
| **E501** — wrap lines > 79 chars (23 spots) | ✅ Applied | Wrapped the out-of-range `return` tuple, a `@pytest.mark.parametrize` list, and a `json.dumps(...)` call; shortened a few comments / `# --- ---` separators. |
| **Naming** — rename any non-conforming identifiers | ✅ None needed | `pyflakes` found no issues; code already uses `snake_case` functions and `UPPER_SNAKE_CASE` constants (`HINTS`, `ATTEMPT_LIMITS`, `DEFAULT_HIGH_SCORE_PATH`). |

All changes were formatting-only — no behavior changed. Verified after the pass:
**50 pytest tests pass** and the `logic_utils.py` **doctests pass**.
