import json

import pytest

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    load_high_scores,
    parse_guess,
    proximity_label,
    save_high_scores,
    update_high_scores,
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


# --- Bug 1: backwards hints --------------------------------------------------
# A guess that is ABOVE the secret must never be reported as "Too Low" (and
# vice-versa). This locks in the high/low direction so the lie can't return.


def test_high_guess_is_never_too_low():
    assert check_guess(99, 1) == "Too High"


def test_low_guess_is_never_too_high():
    assert check_guess(1, 99) == "Too Low"


# --- Bug 6: secret must stay an int, not be compared as a string -------------
# The old code stringified the secret on even attempts, which made comparisons
# unreliable. check_guess should give a stable, numeric result every time.


def test_check_guess_is_numeric_not_string_compare():
    # As strings "100" < "20" would flip the hint; numerically 100 > 20.
    assert check_guess(100, 20) == "Too High"


# --- Bug 3: invalid input must be rejected (can't consume an attempt) --------


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


# --- Bug 8 & 9: each difficulty must report its own range --------------------


def test_range_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)


def test_range_normal():
    assert get_range_for_difficulty("Normal") == (1, 100)


def test_range_hard():
    assert get_range_for_difficulty("Hard") == (1, 50)


# --- Scoring: a wrong guess should cost points, regardless of direction ------


def test_wrong_guess_loses_points():
    assert update_score(50, "Too High", 1) == 45
    assert update_score(50, "Too Low", 1) == 45


# === Edge cases: parse_guess must handle these gracefully (never crash) ======

# --- Edge case 1: infinities / overflow inputs -------------------------------
# "inf" and "1e999" used to reach int(float(...)) and raise OverflowError,
# which the old `except ValueError` did NOT catch -> the app crashed. These
# must now be rejected with a clean error and no exception.


@pytest.mark.parametrize(
    "raw",
    ["inf", "Inf", "-inf", "infinity", "1e999", "1E999", "nan", "NaN"],
)
def test_parse_guess_rejects_inf_and_nan(raw):
    ok, value, err = parse_guess(raw)
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_parse_guess_does_not_raise_on_infinity():
    # The real regression: this must return, not raise OverflowError.
    try:
        parse_guess("1e999")
    except Exception as exc:  # pragma: no cover - failure path
        pytest.fail(f"parse_guess crashed on 'inf'-like input: {exc!r}")


def test_parse_guess_accepts_plain_scientific_notation():
    # A finite exponent is still a legitimate whole number.
    ok, value, err = parse_guess("1e3")
    assert ok is True and value == 1000 and err is None


# --- Edge case 2: out-of-range numbers (negatives & extremely large) ---------
# parse_guess validated "is it a number" but never "is it in range", so -50 or
# 999999 counted as real guesses. With low/high supplied they must be rejected.


@pytest.mark.parametrize("raw", ["-50", "0", "21", "999999"])
def test_parse_guess_rejects_out_of_range(raw):
    ok, value, err = parse_guess(raw, low=1, high=20)
    assert ok is False
    assert value is None
    assert "Out of range" in err


@pytest.mark.parametrize("raw,expected", [("1", 1), ("20", 20), ("13", 13)])
def test_parse_guess_accepts_in_range_boundaries(raw, expected):
    ok, value, err = parse_guess(raw, low=1, high=20)
    assert ok is True and value == expected and err is None


def test_parse_guess_without_range_still_accepts_large_int():
    # No bounds given -> range check is skipped (backwards compatible).
    ok, value, err = parse_guess("999999999")
    assert ok is True and value == 999999999 and err is None


# --- Edge case 3: decimals must not silently truncate ------------------------
# "42.9" used to become 42, so a fractional guess could "win". A fractional
# value is now rejected; a whole-valued decimal like "42.0" is still accepted.


@pytest.mark.parametrize("raw", ["42.9", "-0.5", "19.99", "0.1"])
def test_parse_guess_rejects_fractional_decimals(raw):
    ok, value, err = parse_guess(raw)
    assert ok is False
    assert value is None
    assert err == "Enter a whole number."


@pytest.mark.parametrize("raw,expected", [("42.0", 42), ("7.000", 7)])
def test_parse_guess_accepts_whole_valued_decimals(raw, expected):
    ok, value, err = parse_guess(raw)
    assert ok is True and value == expected and err is None


def test_fractional_decimal_is_rejected_even_when_in_range():
    # Range-checking must not accidentally let a fraction through.
    ok, value, err = parse_guess("12.5", low=1, high=20)
    assert ok is False and value is None and err == "Enter a whole number."


# === Feature: High Score tracker =============================================

# --- update_high_scores: pure record logic -----------------------------------


def test_first_score_is_always_a_record():
    scores, is_record = update_high_scores({}, "Easy", 50)
    assert is_record is True
    assert scores == {"Easy": 50}


def test_higher_score_replaces_and_is_a_record():
    scores, is_record = update_high_scores({"Easy": 50}, "Easy", 80)
    assert is_record is True
    assert scores["Easy"] == 80


def test_lower_score_is_not_a_record():
    scores, is_record = update_high_scores({"Easy": 80}, "Easy", 30)
    assert is_record is False
    assert scores["Easy"] == 80


def test_equal_score_is_not_a_record():
    # Must strictly beat the previous best to count.
    scores, is_record = update_high_scores({"Easy": 80}, "Easy", 80)
    assert is_record is False
    assert scores["Easy"] == 80


def test_scores_are_tracked_per_difficulty():
    scores, _ = update_high_scores({"Easy": 80}, "Hard", 40)
    assert scores == {"Easy": 80, "Hard": 40}


def test_update_does_not_mutate_input_dict():
    original = {"Easy": 50}
    update_high_scores(original, "Easy", 90)
    assert original == {"Easy": 50}  # caller's dict left untouched


# --- load/save round trip and graceful failure ------------------------------


def test_save_then_load_round_trip(tmp_path):
    path = str(tmp_path / "high_scores.json")
    assert save_high_scores({"Easy": 70, "Hard": 40}, path) is True
    assert load_high_scores(path) == {"Easy": 70, "Hard": 40}


def test_load_missing_file_returns_empty(tmp_path):
    path = str(tmp_path / "does_not_exist.json")
    assert load_high_scores(path) == {}


def test_load_corrupt_file_returns_empty(tmp_path):
    path = tmp_path / "high_scores.json"
    path.write_text("{ this is not valid json", encoding="utf-8")
    assert load_high_scores(str(path)) == {}


def test_load_non_dict_json_returns_empty(tmp_path):
    path = tmp_path / "high_scores.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    assert load_high_scores(str(path)) == {}


def test_load_drops_non_integer_values(tmp_path):
    path = tmp_path / "high_scores.json"
    path.write_text(
        json.dumps({"Easy": 70, "Hard": "oops", "Normal": 55}),
        encoding="utf-8",
    )
    assert load_high_scores(str(path)) == {"Easy": 70, "Normal": 55}


# === Feature: Hot/Cold proximity label =======================================
# Cosmetic only — must never affect scoring or the win/lose decision.


def test_exact_match_is_bullseye():
    assert proximity_label(50, 50, 1, 100) == ("Bullseye", "🎯")


def test_very_close_guess_is_hot():
    # 2 away on a span of 99 -> ~2% -> Hot.
    state, emoji = proximity_label(52, 50, 1, 100)
    assert state == "Hot" and emoji == "🔥"


def test_far_guess_is_cold():
    state, emoji = proximity_label(5, 90, 1, 100)
    assert state == "Cold" and emoji == "🧊"


@pytest.mark.parametrize(
    "guess,expected",
    [(52, "Hot"), (60, "Warm"), (75, "Cool"), (95, "Cold")],
)
def test_proximity_bands_scale_with_range(guess, expected):
    # secret 50 on 1-100: distance/99 picks the band.
    state, _ = proximity_label(guess, 50, 1, 100)
    assert state == expected


def test_proximity_is_relative_to_range_size():
    # Same absolute distance (2) reads "hotter" on a small range than a large
    # one: ~10% of Easy's span (Warm) vs ~2% of Normal's span (Hot).
    assert proximity_label(12, 10, 1, 20)[0] == "Warm"
    assert proximity_label(52, 50, 1, 100)[0] == "Hot"


def test_proximity_handles_degenerate_range():
    # A zero-width range must not raise (ZeroDivisionError) on a wrong guess.
    state, _ = proximity_label(7, 5, 5, 5)
    assert state == "Cold"
