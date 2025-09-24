"""Tests for expense formatter helpers."""
from datetime import datetime

import pytest

from expanses_tracker.application.models.expense import ExpenseSchema
from expanses_tracker.application.utils.expense_formatter import format_recent_expenses


def _expense(**kwargs) -> ExpenseSchema:
    """Convenience helper to build ExpenseSchema instances for tests."""
    defaults = dict(
        msg_id=1,
        chat_id=1,
        user_id=1,
        amount=10.0,
        description="Item",
        date=datetime(2024, 5, 20),
        type=None,
        category=None,
    )
    defaults.update(kwargs)
    return ExpenseSchema.model_construct(**defaults)


def test_format_recent_expenses_empty_list() -> None:
    assert format_recent_expenses([]) == "<pre>No expenses recorded yet.</pre>"


def test_format_recent_expenses_renders_multiple_entries() -> None:
    expenses = [
        _expense(
            msg_id=1,
            amount=10.5,
            description="Coffee",
            type="need",
            category="food",
            date=datetime(2024, 5, 20),
        ),
        _expense(
            msg_id=2,
            amount=2,
            description="Milk",
            date=datetime(2024, 5, 19),
        ),
    ]

    result = format_recent_expenses(expenses)

    assert result == "Last expenses:\n<pre>05-20 | 10.5 | Coffee | need | food\n05-19 | 2 | Milk</pre>"


def test_format_recent_expenses_escapes_html_characters() -> None:
    expenses = [
        _expense(description="Tea & Honey", category="<sweet>")
    ]

    result = format_recent_expenses(expenses)

    assert "Tea &amp; Honey" in result
    assert "&lt;sweet&gt;" in result
