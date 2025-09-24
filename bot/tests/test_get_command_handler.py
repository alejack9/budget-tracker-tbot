"""Tests covering the /get command handler."""
from __future__ import annotations

import asyncio
from contextlib import nullcontext
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from telegram.constants import ParseMode

from expanses_tracker.application.features.get_expenses.get_command_handler import (
    DEFAULT_LIMIT,
    get_command_handler,
)
from expanses_tracker.application.models.expense import ExpenseSchema
from expanses_tracker.application.utils.expense_formatter import format_recent_expenses
from expanses_tracker.persistence.database_context.database import DatabaseFactory
from expanses_tracker.persistence.repositories.repository import ExpenseRepository


def _expense(**kwargs) -> ExpenseSchema:
    data = dict(
        msg_id=1,
        chat_id=1,
        user_id=2,
        amount=12.5,
        description="Coffee",
        date=datetime(2024, 5, 21),
    )
    data.update(kwargs)
    return ExpenseSchema.model_construct(**data)


def test_get_command_handler_uses_default_limit(monkeypatch):
    message = AsyncMock()
    message.message_id = 11
    update = SimpleNamespace(
        message=message,
        effective_chat=SimpleNamespace(id=1),
        effective_user=SimpleNamespace(id=2),
    )
    context = SimpleNamespace(args=[])

    session = object()
    monkeypatch.setattr(DatabaseFactory, "get_session", lambda: nullcontext(session))

    captured = {}

    def fake_get_last_expenses(*, session: object, chat_id: int, user_id: int, limit: int):
        captured.update(session=session, chat_id=chat_id, user_id=user_id, limit=limit)
        return [_expense()]

    monkeypatch.setattr(ExpenseRepository, "get_last_expenses", fake_get_last_expenses)

    asyncio.run(get_command_handler(update, context))

    assert captured["session"] is session
    assert captured["chat_id"] == 1
    assert captured["user_id"] == 2
    assert captured["limit"] == DEFAULT_LIMIT

    expected_text = format_recent_expenses([_expense()])
    message.reply_text.assert_awaited_once_with(
        expected_text,
        reply_to_message_id=11,
        parse_mode=ParseMode.HTML,
    )


def test_get_command_handler_rejects_invalid_argument(monkeypatch):
    message = AsyncMock()
    message.message_id = 22
    update = SimpleNamespace(
        message=message,
        effective_chat=SimpleNamespace(id=1),
        effective_user=SimpleNamespace(id=2),
    )
    context = SimpleNamespace(args=["bad"])

    def fail_get_session():  # pragma: no cover - should not be called
        raise AssertionError("DB should not be touched on invalid input")

    monkeypatch.setattr(DatabaseFactory, "get_session", fail_get_session)
    monkeypatch.setattr(ExpenseRepository, "get_last_expenses", lambda **_: [])

    asyncio.run(get_command_handler(update, context))

    message.reply_text.assert_awaited_once_with(
        "Please provide a positive number, e.g. /get 5.",
        reply_to_message_id=22,
    )
