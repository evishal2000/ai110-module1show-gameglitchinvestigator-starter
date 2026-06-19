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

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
  Claude

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
