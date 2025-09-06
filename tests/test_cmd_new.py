import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

# allow importing the bot module
sys.path.append(str(Path(__file__).resolve().parents[1]))

# ensure BOT_TOKEN env var for module import
os.environ.setdefault("BOT_TOKEN", "TEST_TOKEN")

from bot.bot import cmd_new

class DummyChat:
    def __init__(self, message):
        self.message = message
        self.sent = []

    async def send_message(self, text):
        self.sent.append(text)

class DummyMessage:
    def __init__(self, text, date):
        self.text = text
        self.date = date
        self.replies = []

    async def reply_text(self, text):
        self.replies.append(text)

class DummyUser:
    def __init__(self, uid=123):
        self.id = uid

class DummyUpdate:
    def __init__(self, text, date):
        self.message = DummyMessage(text, date)
        self.effective_user = DummyUser()
        self.effective_chat = DummyChat(self.message)


def run(coro):
    return asyncio.run(coro)


def test_cmd_new_without_date():
    dt = datetime(2024, 1, 2)
    upd = DummyUpdate("/new 10 coffee", dt)
    run(cmd_new(upd, None))
    assert len(upd.message.replies) == 1
    data = json.loads(upd.message.replies[0])
    assert data == {
        "date": dt.date().isoformat(),
        "amount": 10.0,
        "description": "coffee",
        "category": "",
        "type": "",
    }


def test_cmd_new_with_date_and_year_default():
    msg_date = datetime(2024, 5, 4)
    upd = DummyUpdate("/new 01/02 5 lunch food", msg_date)
    run(cmd_new(upd, None))
    data = json.loads(upd.message.replies[0])
    assert data == {
        "date": "2024-02-01",
        "amount": 5.0,
        "description": "lunch",
        "category": "food",
        "type": "",
    }


def test_cmd_new_invalid_date():
    msg_date = datetime(2024, 1, 1)
    upd = DummyUpdate("/new 31/02 5 lunch", msg_date)
    run(cmd_new(upd, None))
    assert upd.message.replies == ["Ambiguous command. Invalid date."]


def test_cmd_new_missing_parameters():
    msg_date = datetime(2024, 1, 1)
    upd = DummyUpdate("/new 10", msg_date)
    run(cmd_new(upd, None))
    assert upd.message.replies == ["Ambiguous command. Not enough parameters."]


def test_cmd_new_unquoted_description_warning():
    msg_date = datetime(2024, 1, 1)
    upd = DummyUpdate("/new 5 too many words here", msg_date)
    run(cmd_new(upd, None))
    assert upd.message.replies == ["Ambiguous command. Please quote description if it contains spaces."]
