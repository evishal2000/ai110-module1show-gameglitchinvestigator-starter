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

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
