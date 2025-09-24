"""Helpers for turning expense data into user-facing strings."""
from __future__ import annotations

from html import escape
from typing import Sequence

from expanses_tracker.application.models.expense import ExpenseSchema


def format_recent_expenses(expenses: Sequence[ExpenseSchema]) -> str:
    """Return a short, human readable summary of the most recent expenses."""
    if not expenses:
        return "<pre>No expenses recorded yet.</pre>"

    lines = []
    for expense in expenses:
        date_value = expense.date.strftime("%m-%d")
        amount_value = _format_amount(expense.amount)
        items = [date_value, amount_value, expense.description]
        if expense.type:
            items.append(expense.type)
        if expense.category:
            items.append(expense.category)
        lines.append(" | ".join(items))

    escaped_lines = [escape(line) for line in lines]
    return "Last expenses:\n<pre>" + "\n".join(escaped_lines) + "</pre>"


def _format_amount(amount: float) -> str:
    text = f"{amount:.2f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text
