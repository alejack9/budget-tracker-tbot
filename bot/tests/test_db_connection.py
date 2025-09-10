#!/usr/bin/env python3
"""
Simple script to verify that the database configuration is working correctly.
"""
import os
import sys
import logging

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.expanses_tracker_tbot.data import DatabaseFactory, ExpenseModel, init_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_db_connection():
    """Test the database connection using the environment variable."""
    # If no DATABASE_URL is set, this will raise an error
    try:
        # Get the connection URL from the environment
        url = DatabaseFactory.get_connection_url()
        logger.info(f"Database URL: {url}")
        
        # Get the database engine name
        engine_name = DatabaseFactory.get_engine_name()
        logger.info(f"Using database engine: {engine_name}")
        
        # Initialize the database
        init_db()
        logger.info("Database connection successful!")
        
        # Create a session and test a query
        session = DatabaseFactory.get_session()
        try:
            # Try a simple query to verify connection
            result = session.query(ExpenseModel).limit(1).all()
            logger.info(f"Query executed successfully! Found {len(result)} records.")
            
            # Show table metadata
            from sqlalchemy import inspect
            inspector = inspect(DatabaseFactory._DatabaseFactory__engine)
            tables = inspector.get_table_names()
            logger.info(f"Available tables: {tables}")
            
            return True
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return False
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if DATABASE_URL is set
    if "DATABASE_URL" not in os.environ:
        logger.error("DATABASE_URL environment variable is not set!")
        logger.info("Example: export DATABASE_URL=sqlite:///expenses.db")
        sys.exit(1)
    
    # Test the connection
    success = test_db_connection()
    sys.exit(0 if success else 1)
