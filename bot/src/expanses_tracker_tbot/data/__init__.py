from expanses_tracker_tbot.data.database import DatabaseFactory, Base
from expanses_tracker_tbot.data.models import ExpenseModel, ExpenseSchema
from expanses_tracker_tbot.data.repository import ExpenseRepository

__all__ = [
    "DatabaseFactory",
    "Base",
    "ExpenseModel",
    "ExpenseSchema",
    "ExpenseRepository",
]

# Initialize the database connection
def init_db():
    DatabaseFactory.init_db()
    DatabaseFactory.create_tables()
