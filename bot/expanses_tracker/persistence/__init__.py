# Initialize the database connection
from bot.expanses_tracker.persistence.database_context.database import DatabaseFactory

def persistence_registration():
    DatabaseFactory.init_db()
    DatabaseFactory.create_tables()
