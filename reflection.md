# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
   (for example: "the hints were backwards").
  -> the hints were backwards
  -> the newgame is not working had to force restart to start a new game
  ->Attempts are not being tracked properky
  --> the input is tracking the previous value
  --> the developer debug info its one submit behind
  --> the selected difficulty is not stored in session state before submit
  --> the on-screen range always says 1 to 100 even for Easy/Hard
  --> changing difficulty mid-game can leave the secret outside the displayed range

| #   | Bug                        | Input Used                      | Expected Behavior                             | Actual Behavior                                                         | Console Error                |
| --- | -------------------------- | ------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------- |
| 1   | Backwards hints            | Guess `60`, secret `42`         | `📉 Go LOWER!`                                | `📈 Go HIGHER!` shown                                                  | none                         |
| 2   | New Game dead              | `New Game 🔁` after game over   | Fresh round starts                            | Stuck on "Game over" screen                                            | none                         |
| 3   | Attempt mistracked         | Submit empty box / `abc`        | No attempt used                               | "Attempts left" still drops by 1                                       | none (UI: `Enter a guess.`)  |
| 4   | Input not cleared          | Type `30`, Submit               | Box clears                                    | Box still shows `30`                                                   | none                         |
| 5   | Debug one behind           | Guess `42`, debug open          | `History` includes `42`                       | Shows previous list, no `42`                                           | none                         |
| 6   | Secret cast to string      | 2nd (even) guess `60`           | Same number-based hint                        | Hint unreliable (string compare)                                       | none (`TypeError` swallowed) |
| 7   | Difficulty state missing   | Submit guess after page load    | Submit uses selected difficulty without crash | App can raise `KeyError` because `st.session_state.difficulty` is unset | yes                          |
| 8   | Hardcoded range prompt     | Select Easy or Hard             | Prompt shows the selected range               | Prompt still displays `1 to 100`                                       | none                         |
| 9   | Difficulty change mismatch | Change difficulty during a game | Secret and attempts reset for the new range   | Secret may remain outside the new range                                | none                         |

---

## 2. How did you use AI as a teammate?

I used **Claude (in Claude Code / agent mode)** as my main AI teammate on this project. I treated it like a pair-programming partner: I described each bug from my list and asked it to explain the cause before changing anything, rather than just letting it rewrite the file.

- **A suggestion that was correct:** When the "New Game" button looked dead, I asked why the game stayed stuck on the game-over screen. Claude pointed out that `start_new_round` reset the secret and attempts but never reset `status`, so the `st.stop()` guard fired immediately after the rerun. I verified this by adding the status reset, then actually clicking through a full lose → New Game cycle in the running app and confirming a fresh round started.
- **A suggestion that was misleading:** For clearing the input box after a guess, the first approach we reached for was calling `st.rerun()` right after submitting. That technically cleared the box, but it also wiped the "Go HIGHER/LOWER" hint message before I could read it. I caught this by testing it live, and we switched to an `on_click` callback that stores the feedback in `session_state` and clears the box — so the message survives the rerun.

---

## 3. Debugging and testing your fixes

- **How I decided a bug was really fixed:** For pure logic bugs I relied on `pytest` going green, and for the UI/state bugs I reproduced the exact steps from my bug table and watched the Developer Debug Info panel to confirm the secret, attempts, and status behaved correctly.
- **A test I ran:** I ran `pytest` and specifically added cases that target the backwards-hint bug, like `check_guess(60, 50)` asserting `"Too High"` and `check_guess(100, 20)` asserting `"Too High"`. The second one was useful because as strings `"100" < "20"`, so it proved the comparison is truly numeric and not accidentally comparing strings (the old even-attempt bug). All 14 tests passed after the fixes.
- **Did AI help with tests?** Yes — Claude helped me write `parse_guess` tests for empty input, whitespace, and `"abc"`, which map directly to the "attempt mistracked" bug (invalid input should return `ok=False` and never consume a turn). It also diagnosed a `ModuleNotFoundError` when I ran bare `pytest`, explaining that the repo root wasn't on `sys.path`, and we fixed it by adding a root `conftest.py`.
- **Edge-case hardening (beyond the nine bugs):** I then asked which inputs could *still* break the game and found three. The sharpest was `"inf"`/`"1e999"`: the parser did `int(float(raw))`, but `int(float("inf"))` raises `OverflowError`, not `ValueError`, so the existing guard let it crash the whole app. I also found that out-of-range numbers (e.g. `-50`) counted as real guesses and that decimals like `42.9` were silently truncated to `42` (so a "wrong" number could win). I fixed all three — reject inf/nan, range-check before counting an attempt, and reject fractions — and grew the suite from 14 to **39 passing tests**, with parametrized cases pinning each edge case so it can't regress.

---

## 4. What did you learn about Streamlit and state?

The biggest thing I learned is that Streamlit re-runs the *entire* script top-to-bottom on every interaction — every button click, text input, or widget change. I'd explain it to a friend like this: imagine the whole file restarts from line 1 each time you touch anything, so any normal Python variable you set is forgotten instantly. `st.session_state` is the one box that survives those restarts — it's like a backpack the app carries between runs, so that's where the secret number, attempts, and score have to live. The order things run in matters too: because the script flows top-down, my debug panel was "one submit behind" until I moved the guess logic into an `on_click` callback that updates `session_state` *before* the page re-renders. Once I pictured the rerun-from-scratch model, most of the state bugs (the resetting secret, the dead New Game button, the stale debug panel) suddenly made sense as the same root cause.

---

## 5. Looking ahead: your developer habits

- **Habit I want to reuse:** Writing the bug down first — input, expected, and actual — before touching any code. Filling out that bug table forced me to actually reproduce each glitch and gave me a concrete pass/fail check, instead of "fixing" something and hoping. I also want to keep the pattern of pinning logic with `pytest` (like the `check_guess(100, 20)` → `"Too High"` case) so a fix can't silently regress.
- **What I'd do differently with AI:** I'd ask the AI to *explain the cause before writing any code* every single time. A couple of times I let it jump straight to a fix (the `st.rerun()` suggestion that wiped my hint message) and only caught the problem by testing live — if I'd made it justify the approach first, I'd have spotted that it nuked the feedback message before I burned time on it.
- **How this changed my thinking:** I now treat AI-generated code as a confident *draft from a teammate*, not a finished answer — it's fast and often right about the cause, but it will hand you plausible code that's subtly wrong (like comparing strings instead of ints), so I'm the one who has to test it and stay in control.
