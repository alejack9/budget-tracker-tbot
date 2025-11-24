from dependency_injector import containers, providers

from src.application.use_cases.add_expense import AddExpenseUseCase
from src.config.settings import Settings
from src.infrastructure.persistence.sqlalchemy.repositories.expense_repository import (
    SqlAlchemyExpenseRepository,
)
from src.infrastructure.persistence.sqlalchemy.session import SessionLocal


class Container(containers.DeclarativeContainer):
    """Application IoC container configuring infrastructure and use cases."""

    settings = providers.Singleton(Settings)

    session = providers.Factory(SessionLocal)

    expense_repository = providers.Object(
        SqlAlchemyExpenseRepository,)
    
    add_expense_use_case = providers.Factory(
        AddExpenseUseCase)