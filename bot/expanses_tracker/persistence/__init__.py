"""Database initialization and table creation for the expenses tracker application."""

# Initialize the database connection
from expanses_tracker.persistence.database_context.database import DatabaseFactory

def persistence_registration():
    """Register persistence layer by initializing the database and creating necessary tables."""
    DatabaseFactory.init_db()
    DatabaseFactory.create_tables()
