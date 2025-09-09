from __future__ import annotations

from datetime import datetime

from expanses_tracker_tbot.message_parser import get_message_args, get_message_category, __get_message_date, __get_message_type
import pytest

# ---------- get_message_date ----------

def test_get_message_date_no_year():
    parts = ["10", "spesa", "21/05"]
    default = datetime(2025, 9, 9)
    dt, rest = __get_message_date(parts, default)
    assert dt == datetime(2025, 5, 21)
    assert rest == ["10", "spesa"]  # last token popped


def test_get_message_date_with_year():
    parts = ["10", "spesa", "21/05/2023"]
    default = datetime(2025, 9, 9)
    dt, rest = __get_message_date(parts, default)
    assert dt == datetime(2023, 5, 21)
    assert rest == ["10", "spesa"]


def test_get_message_date_not_a_date_leaves_parts():
    parts = ["10", "spesa", "yesterday"]
    default = datetime(2025, 9, 9)
    dt, rest = __get_message_date(parts, default)
    assert dt == default
    assert rest is parts and rest == ["10", "spesa", "yesterday"]


def test_get_message_date_invalid_date_raises():
    parts = ["10", "spesa", "31/02"]  # matches regex, invalid calendar date
    default = datetime(2025, 9, 9)
    with pytest.raises(ValueError, match="Ambiguous command. Invalid date."):
        __get_message_date(parts, default)
    # ensure it didn't pop the invalid token
    assert parts == ["10", "spesa", "31/02"]


# ---------- get_message_domain / type / category ----------

def test_get_message_type_pops_last_case_insensitive():
    parts = ["foo", "NEED"]
    t, rest = __get_message_type(parts)
    assert t == "need"
    assert rest == ["foo"]


def test_get_message_category_pops_last():
    parts = ["foo", "food"]
    c, rest = get_message_category(parts)
    assert c == "food"
    assert rest == ["foo"]


def test_get_message_domain_no_match():
    parts = ["foo"]
    c, rest = get_message_category(parts)
    assert c is None
    assert rest == ["foo"]


# ---------- get_message_args (end-to-end) ----------

@pytest.mark.parametrize(
    "text, default_dt, expected",
    [
        (
            "10 spesa",
            datetime(2025, 9, 9),
            dict(amount=10.0, description="spesa", type=None, category=None, date=datetime(2025, 9, 9)),
        ),
        (
            '10.5 "spesa casa" food need',
            datetime(2025, 9, 9),
            dict(amount=10.5, description="spesa casa", type="need", category="food", date=datetime(2025, 9, 9)),
        ),
        (
            "10/2 spesa",
            datetime(2025, 9, 9),
            dict(amount=5.0, description="spesa", type=None, category=None, date=datetime(2025, 9, 9)),
        ),
        (
            "10 spesa 21/05",
            datetime(2025, 9, 9),
            dict(amount=10.0, description="spesa", type=None, category=None, date=datetime(2025, 5, 21)),
        ),
        (
            "10 spesa food need 21/05",
            datetime(2025, 9, 9),
            dict(amount=10.0, description="spesa", type="need", category="food", date=datetime(2025, 5, 21)),
        ),
        (
            "10 spesa 21/05/1999",
            datetime(2025, 9, 9),
            dict(amount=10.0, description="spesa", type=None, category=None, date=datetime(1999, 5, 21)),
        ),
    ],
)
def test_get_message_args_happy_paths(text, default_dt, expected):
    out = get_message_args(text, default_dt)
    assert out.amount == pytest.approx(expected["amount"])
    assert out.description == expected["description"]
    assert out.type == expected["type"]
    assert out.category == expected["category"]
    assert out.date == expected["date"]


@pytest.mark.parametrize(
    "text, err_re",
    [
        ("spesa", r"Not enough parameters"),
        ("10", r"Not enough parameters"),
        ("abc spesa", r"Invalid amount"),
        ("10//2 spesa", r"Invalid amount"),
        ("10/0 spesa", r"Division by zero in amount."),  # division by zero currently surfaces as "Invalid amount"
        ("10 spesa 31/02", r"Invalid date"),
        ("", r"Not enough parameters"),
    ],
)
def test_get_message_args_errors(text, err_re):
    with pytest.raises(ValueError, match=err_re):
        get_message_args(text, datetime(2025, 9, 9))


def test_type_after_category_is_not_parsed():
    # "type" must be the last token when both are present (expected input: "<...> <category> <type>").
    out = get_message_args("10 spesa need food", datetime(2025, 9, 9))
    # Category recognized (food), type left in description (limitation by design/order).
    assert out.category == "food"
    assert out.type is None
    assert out.description == "spesa need"
    assert out.amount == pytest.approx(10.0)
