from dependency_injector import containers, providers

from src.application.use_cases.add_expense import AddExpenseUseCase
from src.config.settings import Settings
from src.infrastructure.persistence.sqlalchemy.repositories.expense_repository import (
    SqlAlchemyExpenseRepository,
)
from src.infrastructure.persistence.sqlalchemy.session import (
    build_engine,
    build_session_factory,
    create_session,
    get_session,
)


class Container(containers.DeclarativeContainer):
    """Application IoC container configuring infrastructure and use cases."""

    settings = providers.Singleton(Settings)

    engine = providers.Singleton(build_engine, settings=settings)

    session_factory = providers.Singleton(build_session_factory, engine=engine)

    session = providers.Factory(create_session, factory=session_factory)

    session_scope = providers.Resource(get_session, factory=session_factory)

    expense_repository = providers.Factory(
        SqlAlchemyExpenseRepository,
        session=session,
    )

    add_expense_use_case = providers.Factory(
        AddExpenseUseCase,
        expense_repo=expense_repository,
    )