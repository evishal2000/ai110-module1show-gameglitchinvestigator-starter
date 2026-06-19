# FIX: Refactored the four core functions out of app.py into this module using
# Claude (agent mode). I described the README's "move logic into logic_utils.py"
# task; the AI ported the functions and I verified each against pytest.

def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Hard":
        return 1, 50
    # Normal (and any unknown value) defaults to the standard range.
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    raw = raw.strip()
    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except ValueError:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome.

    outcome is one of: "Win", "Too High", "Too Low"
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
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        # Fewer attempts -> more points, with a floor of 10.
        points = 100 - 10 * (attempt_number - 1)
        return current_score + max(points, 10)

    # A wrong guess costs 5 points.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
