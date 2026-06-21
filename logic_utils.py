"""Core game logic for the Number Guessing Game.

This module holds the pure, UI-independent logic for the Streamlit app in
``app.py``: difficulty ranges, input parsing/validation, guess evaluation,
scoring, and the persistent high-score tracker. Keeping it free of Streamlit
imports lets every function be unit-tested directly with ``pytest`` (see
``tests/test_game_logic.py``).
"""

import json
import math

# FIX: Refactored the four core functions out of app.py into this module using
# Claude (agent mode). I described the README's "move logic into logic_utils"
# task; the AI ported the functions and I verified each against pytest.


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive guessing range for a difficulty level.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``. Any
            unrecognized value falls back to the Normal range.

    Returns:
        tuple[int, int]: The ``(low, high)`` bounds, both inclusive.
            ``"Easy"`` -> ``(1, 20)``, ``"Hard"`` -> ``(1, 50)``,
            everything else -> ``(1, 100)``.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("???")
        (1, 100)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Hard":
        return 1, 50
    # Normal (and any unknown value) defaults to the standard range.
    return 1, 100


def parse_guess(raw: str, low=None, high=None):
    """Parse and validate raw user input into an integer guess.

    Validation never raises; every rejected input returns a human-readable
    error message instead, so the caller can surface it without a try/except.

    Args:
        raw: The raw string entered by the player (may be ``None``, empty,
            or surrounded by whitespace).
        low: Optional inclusive lower bound. When both ``low`` and ``high``
            are provided, values outside ``[low, high]`` are rejected.
        high: Optional inclusive upper bound (see ``low``).

    Returns:
        tuple[bool, int | None, str | None]: A ``(ok, guess, error)`` triple.
            On success, ``(True, <int>, None)``. On failure,
            ``(False, None, <message>)``.

    Notes:
        Edge cases are handled gracefully rather than crashing:
            * ``""`` / whitespace / ``None`` -> ``"Enter a guess."``
            * non-numeric text, ``"inf"``, ``"1e999"``, ``"nan"``
              -> ``"That is not a number."``
            * fractional decimals such as ``"42.9"`` -> ``"Enter a whole
              number."`` (this is a whole-number game; values are not
              silently truncated)
            * out-of-range values (when bounds given)
              -> ``"Out of range. Pick a number between {low} and {high}."``

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("42.0")
        (True, 42, None)
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
        >>> parse_guess("99", low=1, high=20)
        (False, None, 'Out of range. Pick a number between 1 and 20.')
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    raw = raw.strip()
    try:
        # Anything that could carry a fraction/exponent goes through float()
        # first so we can inspect it, rather than blindly truncating.
        if "." in raw or "e" in raw.lower():
            value = float(raw)
        else:
            value = int(raw)
    except (ValueError, OverflowError):
        # OverflowError can't actually escape here anymore, but we keep it in
        # the guard so a future int(float(...)) path can never crash the app.
        return False, None, "That is not a number."

    if isinstance(value, float):
        # inf / -inf / nan survive float() but are not real guesses.
        if math.isinf(value) or math.isnan(value):
            return False, None, "That is not a number."
        # This is a whole-number game: reject fractions instead of silently
        # truncating "42.9" into 42.
        if value != int(value):
            return False, None, "Enter a whole number."
        value = int(value)

    if low is not None and high is not None and not (low <= value <= high):
        return (
            False,
            None,
            f"Out of range. Pick a number between {low} and {high}.",
        )

    return True, value, None


def check_guess(guess, secret):
    """Compare a guess against the secret number.

    Both arguments must be numeric; comparison is done numerically (not as
    strings) so the high/low direction is always correct.

    Args:
        guess: The player's numeric guess.
        secret: The secret number to match.

    Returns:
        str: ``"Win"`` if equal, ``"Too High"`` if the guess exceeds the
            secret, otherwise ``"Too Low"``.

    Examples:
        >>> check_guess(50, 50)
        'Win'
        >>> check_guess(60, 50)
        'Too High'
        >>> check_guess(40, 50)
        'Too Low'
    """
    # FIX: Pair-debugged the high/low bug with the AI. It spotted that the
    # original returned the wrong direction; I confirmed with the failing
    # pytest cases that guess > secret must map to "Too High".
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Apply the score change for a single guess outcome.

    A win awards points that decay with the number of attempts (so faster
    wins score higher), with a floor of 10. A wrong guess costs a flat 5
    points. Any other outcome leaves the score unchanged.

    Args:
        current_score: The score before this guess.
        outcome: The result from :func:`check_guess` — ``"Win"``,
            ``"Too High"``, or ``"Too Low"``.
        attempt_number: The 1-based attempt count for this guess (used only
            for the win bonus).

    Returns:
        int: The updated score.

    Examples:
        >>> update_score(0, "Win", 1)      # first-try win: 100 points
        100
        >>> update_score(0, "Win", 4)      # 100 - 10*3 = 70
        70
        >>> update_score(50, "Too High", 2)
        45
    """
    if outcome == "Win":
        # Fewer attempts -> more points, with a floor of 10.
        points = 100 - 10 * (attempt_number - 1)
        return current_score + max(points, 10)

    # A wrong guess costs 5 points.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score


def proximity_label(guess: int, secret: int, low: int, high: int):
    """Describe how close a guess is to the secret as a Hot/Cold state.

    The distance is judged relative to the size of the guessing range, so the
    same label means roughly the same "closeness" on Easy (1-20) as on Normal
    (1-100). This is purely cosmetic feedback and does not affect scoring or
    the win/lose decision.

    Args:
        guess: The player's guess.
        secret: The secret number.
        low: Inclusive lower bound of the range.
        high: Inclusive upper bound of the range.

    Returns:
        tuple[str, str]: A ``(state, emoji)`` pair. An exact match is
            ``("Bullseye", "🎯")``; otherwise one of ``"Hot"`` 🔥,
            ``"Warm"`` ♨️, ``"Cool"`` 🌤️, or ``"Cold"`` 🧊, chosen by how
            small the distance is as a fraction of the range.

    Examples:
        >>> proximity_label(50, 50, 1, 100)
        ('Bullseye', '🎯')
        >>> proximity_label(52, 50, 1, 100)
        ('Hot', '🔥')
        >>> proximity_label(5, 90, 1, 100)
        ('Cold', '🧊')
    """
    distance = abs(guess - secret)
    if distance == 0:
        return "Bullseye", "🎯"

    span = high - low
    ratio = distance / span if span else 1.0
    if ratio <= 0.05:
        return "Hot", "🔥"
    if ratio <= 0.15:
        return "Warm", "♨️"
    if ratio <= 0.30:
        return "Cool", "🌤️"
    return "Cold", "🧊"


# --- High Score tracker ------------------------------------------------------
# FEATURE: persist the best winning score per difficulty across sessions. The
# pure update logic lives here (easy to pytest); file I/O is kept in thin,
# fault-tolerant wrappers so a missing/corrupt file can never crash the app.

DEFAULT_HIGH_SCORE_PATH = "high_scores.json"


def update_high_scores(scores, difficulty: str, score: int):
    """Record a score for a difficulty if it beats the stored best.

    Pure function — performs no file I/O and does not mutate the input
    mapping; it returns a new dict. A higher score is better, and the first
    score recorded for a difficulty always counts as a new record. A score
    that merely ties the previous best is not a new record.

    Args:
        scores: The current mapping of ``difficulty -> best score`` (may be
            ``None`` or empty).
        difficulty: The difficulty key to update.
        score: The candidate score for this round.

    Returns:
        tuple[dict, bool]: ``(updated_scores, is_new_record)`` where
            ``updated_scores`` is a new dict and ``is_new_record`` is True
            only if ``score`` strictly beat (or had no) prior best.

    Examples:
        >>> update_high_scores({}, "Easy", 50)
        ({'Easy': 50}, True)
        >>> update_high_scores({"Easy": 80}, "Easy", 30)
        ({'Easy': 80}, False)
    """
    updated = dict(scores) if scores else {}
    previous = updated.get(difficulty)
    if previous is None or score > previous:
        updated[difficulty] = score
        return updated, True
    return updated, False


def load_high_scores(path: str = DEFAULT_HIGH_SCORE_PATH):
    """Load persisted high scores from a JSON file.

    Fault-tolerant by design: any problem reading or parsing the file
    degrades to an empty result rather than raising, so a missing, empty,
    corrupt, or wrongly-shaped file lets the game start with a clean slate.
    Only ``str -> int`` entries are kept; other shapes are dropped.

    Args:
        path: Path to the JSON file. Defaults to
            :data:`DEFAULT_HIGH_SCORE_PATH`.

    Returns:
        dict[str, int]: The mapping of ``difficulty -> best score``, or an
            empty dict if the file is missing, unreadable, or malformed.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}

    if not isinstance(data, dict):
        return {}
    return {
        key: value
        for key, value in data.items()
        if isinstance(key, str) and isinstance(value, int)
    }


def save_high_scores(scores, path: str = DEFAULT_HIGH_SCORE_PATH):
    """Persist high scores to a JSON file.

    Writes the mapping as indented, key-sorted JSON. Any OS-level write
    failure is swallowed and reported via the return value rather than
    raised, so a failed save can never crash the game.

    Args:
        scores: The ``difficulty -> best score`` mapping to persist.
        path: Destination path. Defaults to :data:`DEFAULT_HIGH_SCORE_PATH`.

    Returns:
        bool: ``True`` if the file was written successfully, ``False`` if an
            :class:`OSError` occurred.
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, sort_keys=True)
        return True
    except OSError:
        return False
