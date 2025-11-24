# src/infrastructure/persistence/sqlalchemy/__init__.py
from .expense_orm import ExpenseORM

__all__ = [
    "ExpenseORM",
]
