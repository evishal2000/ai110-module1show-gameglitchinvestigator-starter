import random

import streamlit as st

from logic_utils import (
    DEFAULT_HIGH_SCORE_PATH,
    check_guess,
    get_range_for_difficulty,
    load_high_scores,
    parse_guess,
    proximity_label,
    save_high_scores,
    update_high_scores,
    update_score,
)

# FIX (Bug 1): Backwards hints. The AI suggested separating the *outcome* from
# the *message* so the high/low text lives in one place; I mapped "Too High" to
# "Go LOWER!" here and sanity-checked it by playing the game.
HINTS = {
    "Win": "🎉 Correct!",
    "Too High": "📉 Go LOWER!",
    "Too Low": "📈 Go HIGHER!",
}

ATTEMPT_LIMITS = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}


def start_new_round(difficulty):
    """Reset every piece of game state for a fresh round in the given range."""
    # FIX (Bug 2): New Game was "dead" because it never reset `status`. Asked
    # the AI why the game-over screen stuck; it pointed at the missing status
    # reset, so we centralised every reset in one helper used by New Game too.
    low, high = get_range_for_difficulty(difficulty)
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    # FEATURE: detailed per-guess log powering the session summary table.
    st.session_state.guess_log = []
    st.session_state.feedback = None
    st.session_state.difficulty = difficulty
    # FEATURE: clear any "new high score" banner from the previous round.
    st.session_state.new_record = False
    # FIX (Bug 4): clear the guess box for the new round.
    st.session_state[f"guess_input_{difficulty}"] = ""


def handle_submit(difficulty):
    """Process a guess. Runs as a button callback, so state is updated before
    the page re-renders — that keeps the input box and debug panel in sync."""
    # FIX (Bug 5): I asked the AI how to stop the debug panel being "one submit
    # behind". It explained Streamlit reruns top-to-bottom, so it moved the
    # logic into an on_click callback that mutates state before the re-render.
    key = f"guess_input_{difficulty}"
    raw = st.session_state.get(key, "")

    # Pass the difficulty's range so out-of-range numbers (negatives, values
    # past the upper bound) are rejected before they can consume an attempt.
    low, high = get_range_for_difficulty(difficulty)
    ok, guess_int, err = parse_guess(raw, low, high)
    if not ok:
        # FIX (Bug 3): validate BEFORE incrementing so invalid input (empty /
        # "abc") can't consume an attempt — caught this together via the new
        # parse_guess pytest cases.
        st.session_state.feedback = ("error", err)
        return

    st.session_state.attempts += 1
    st.session_state.history.append(guess_int)

    # FIX (Bug 6): the AI flagged that the original stringified the secret on
    # even attempts, breaking comparisons; we now always pass the real int.
    outcome = check_guess(guess_int, st.session_state.secret)
    st.session_state.score = update_score(
        current_score=st.session_state.score,
        outcome=outcome,
        attempt_number=st.session_state.attempts,
    )

    # FEATURE: cosmetic Hot/Cold proximity — does not affect scoring or the
    # win/lose decision, it just makes the hint friendlier.
    prox_state, prox_emoji = proximity_label(
        guess_int, st.session_state.secret, low, high
    )

    # FEATURE: record a structured row for the session summary table.
    st.session_state.guess_log.append(
        {
            "#": st.session_state.attempts,
            "Guess": guess_int,
            "Result": outcome,
            "Proximity": f"{prox_emoji} {prox_state}",
            "Score": st.session_state.score,
        }
    )

    attempt_limit = ATTEMPT_LIMITS[difficulty]
    if outcome == "Win":
        st.session_state.status = "won"
        # FEATURE: a finished win is the only score worth banking. Update the
        # per-difficulty best and persist it only when it's actually a record.
        scores, is_record = update_high_scores(
            st.session_state.high_scores, difficulty, st.session_state.score
        )
        st.session_state.high_scores = scores
        st.session_state.new_record = is_record
        if is_record:
            save_high_scores(scores, DEFAULT_HIGH_SCORE_PATH)
        st.session_state.feedback = (
            "win",
            f"You won! The secret was {st.session_state.secret}. "
            f"Final score: {st.session_state.score}",
        )
    elif st.session_state.attempts >= attempt_limit:
        st.session_state.status = "lost"
        st.session_state.feedback = (
            "lost",
            f"Out of attempts! The secret was {st.session_state.secret}. "
            f"Score: {st.session_state.score}",
        )
    else:
        # FEATURE: pair the directional hint with the Hot/Cold proximity.
        st.session_state.feedback = (
            "hint",
            f"{HINTS[outcome]}  ·  {prox_emoji} {prox_state}",
        )

    # Bug 4: clear the input box after a valid guess.
    st.session_state[key] = ""


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game — now actually playable.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit = ATTEMPT_LIMITS[difficulty]
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FEATURE: load persisted high scores once per session, before the panel below
# renders. Kept separate from start_new_round so "New Game" keeps the records.
if "high_scores" not in st.session_state:
    st.session_state.high_scores = load_high_scores(DEFAULT_HIGH_SCORE_PATH)

# FEATURE: High Score panel — best banked score per difficulty, persisted to
# disk so it survives restarts. The current difficulty is highlighted.
st.sidebar.divider()
st.sidebar.subheader("🏆 High Scores")
saved_scores = st.session_state.get("high_scores", {})
for level in ("Easy", "Normal", "Hard"):
    best = saved_scores.get(level)
    best_text = best if best is not None else "—"
    marker = " ⬅" if level == difficulty else ""
    st.sidebar.caption(f"{level}: {best_text}{marker}")

# First load: set up an initial round.
if "status" not in st.session_state:
    start_new_round(difficulty)

# FIX (Bug 7 & 9): difficulty wasn't tracked in session state, so a mid-game
# change left the secret outside the new range. The AI suggested storing the
# difficulty and resetting on change; I verified the range updates live.
if st.session_state.get("difficulty") != difficulty:
    start_new_round(difficulty)

st.subheader("Make a guess")

# FIX (Bug 8): prompt was hardcoded to "1 and 100". The AI and I replaced the
# literals with the low/high from get_range_for_difficulty.
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

# Show the result of the previous action.
feedback = st.session_state.get("feedback")
if feedback:
    kind, msg = feedback
    if kind == "win":
        st.success(msg)
    elif kind in ("lost", "error"):
        st.error(msg)
    elif kind == "hint" and st.session_state.get("show_hint", True):
        st.warning(msg)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}",
)

col1, col2, col3 = st.columns(3)
with col1:
    st.button(
        "Submit Guess 🚀",
        on_click=handle_submit,
        args=(difficulty,),
        disabled=st.session_state.status != "playing",
    )
with col2:
    # Bug 2: New Game fully resets the round (status included) so play resumes.
    st.button("New Game 🔁", on_click=start_new_round, args=(difficulty,))
with col3:
    show_hint = st.checkbox("Show hint", value=True, key="show_hint")

if st.session_state.status == "won":
    st.success("You won this round. Start a new game to play again.")
    # FEATURE: celebrate a new persisted best for this difficulty.
    if st.session_state.get("new_record"):
        st.balloons()
        st.info(
            f"🏆 New high score for {difficulty}: "
            f"{st.session_state.high_scores[difficulty]}!"
        )
elif st.session_state.status == "lost":
    st.error("Game over. Start a new game to try again.")

# FEATURE: structured session summary. Shows every guess this round with its
# outcome, Hot/Cold proximity, and running score, plus quick metrics on top.
guess_log = st.session_state.get("guess_log", [])
if guess_log:
    st.subheader("📋 Session Summary")
    best_row = min(
        guess_log,
        key=lambda row: abs(row["Guess"] - st.session_state.secret),
    )
    m1, m2, m3 = st.columns(3)
    m1.metric("Guesses", len(guess_log))
    m2.metric("Current Score", st.session_state.score)
    m3.metric("Closest", f"{best_row['Guess']} ({best_row['Proximity']})")
    st.table(guess_log)

# FIX (Bug 5, cont.): rendered AFTER the submit callback runs, so the debug
# panel always reflects current state — no longer one submit behind.
with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

st.divider()
st.caption("Debugged by a human. Production-ready for real this time. 🎉")
