from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# --- Bug 1: backwards hints ---------------------------------------------------
# A guess that is ABOVE the secret must never be reported as "Too Low" (and
# vice-versa). This locks in the high/low direction so the lie can't return.

def test_high_guess_is_never_too_low():
    assert check_guess(99, 1) == "Too High"

def test_low_guess_is_never_too_high():
    assert check_guess(1, 99) == "Too Low"


# --- Bug 6: secret must stay an int, not be compared as a string --------------
# The old code stringified the secret on even attempts, which made comparisons
# unreliable. check_guess should give a stable, numeric result every time.

def test_check_guess_is_numeric_not_string_compare():
    # As strings, "100" < "20", which would flip the hint. Numerically 100 > 20.
    assert check_guess(100, 20) == "Too High"


# --- Bug 3: invalid input must be rejected (so it can't consume an attempt) ---

def test_parse_guess_rejects_empty():
    ok, value, err = parse_guess("")
    assert ok is False and value is None and err == "Enter a guess."

def test_parse_guess_rejects_whitespace():
    ok, value, err = parse_guess("   ")
    assert ok is False and value is None and err == "Enter a guess."

def test_parse_guess_rejects_non_number():
    ok, value, err = parse_guess("abc")
    assert ok is False and value is None and err == "That is not a number."

def test_parse_guess_accepts_valid_int():
    ok, value, err = parse_guess("30")
    assert ok is True and value == 30 and err is None


# --- Bug 8 & 9: each difficulty must report its own range ---------------------

def test_range_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)

def test_range_normal():
    assert get_range_for_difficulty("Normal") == (1, 100)

def test_range_hard():
    assert get_range_for_difficulty("Hard") == (1, 50)


# --- Scoring: a wrong guess should cost points, regardless of direction -------

def test_wrong_guess_loses_points():
    assert update_score(50, "Too High", 1) == 45
    assert update_score(50, "Too Low", 1) == 45
