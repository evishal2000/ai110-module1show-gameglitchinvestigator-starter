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

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
