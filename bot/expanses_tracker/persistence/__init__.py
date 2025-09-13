# Initialize the database connection
from expanses_tracker.persistence.database_context.database import DatabaseFactory

def persistence_registration():
    DatabaseFactory.init_db()
    DatabaseFactory.create_tables()
