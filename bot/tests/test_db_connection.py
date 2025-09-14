#!/usr/bin/env python3
"""Pytest to verify that the database configuration is working correctly."""
import logging
import os

import pytest
from sqlalchemy import inspect

from expanses_tracker.persistence import persistence_registration
from expanses_tracker.persistence.configurations.expense_model import ExpenseModel
from expanses_tracker.persistence.database_context.database import DatabaseFactory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_db_connection():
    """Test the database connection using the environment variable."""
    if "DATABASE_URL" not in os.environ:
        pytest.skip("DATABASE_URL is not set; skipping DB connection test.")

    # Validate URL and log engine name
    url = DatabaseFactory.get_connection_url()
    logger.info("Database URL: %s", url)
    engine_name = DatabaseFactory.get_engine_name()
    logger.info("Using database engine: %s", engine_name)

    # Initialize DB and create tables
    persistence_registration()

    # Query using a session and inspect tables without private access
    with DatabaseFactory.get_session() as session:
        result = session.query(ExpenseModel).limit(1).all()
        logger.info("Query executed successfully! Found %d records.", len(result))

        # Use the session bind (public) instead of a private engine attribute
        engine = session.get_bind()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info("Available tables: %s", tables)

        assert "expenses" in tables

if __name__ == "__main__":
    # Running via pytest is preferred; keep a helpful message if invoked directly.
    raise SystemExit(
        "Run this test with pytest (e.g., `pytest -k test_db_connection`)."
    )
