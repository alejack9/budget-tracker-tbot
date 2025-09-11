import os
from typing import Optional, Dict, Any
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Base class for all models
Base = declarative_base()


class DatabaseFactory:
    """Factory class to create database connections based on environment variables"""
    
    # Connection settings
    __engine = None
    __session_factory = None
    
    # Environment variable name for database connection
    ENV_DB_URL = "DATABASE_URL"
    
    @classmethod
    def get_connection_url(cls) -> str:
        """
        Get the database connection URL from environment variable
        
        Requires the DATABASE_URL environment variable to be set.
        No fallbacks are provided.
        
        Returns:
            str: Database connection URL
        
        Raises:
            ValueError: If DATABASE_URL environment variable is not set
        """
        if direct_url := os.environ.get(cls.ENV_DB_URL):
            return direct_url
        
        raise ValueError(
            f"The {cls.ENV_DB_URL} environment variable is required but was not set. "
            "Please set it to a valid SQLAlchemy connection string. "
            "Examples: 'sqlite:///expenses.db', 'postgresql://user:pass@host:port/dbname'"
        )

    @classmethod
    def create_engine_with_args(cls, **kwargs) -> Engine:
        """Create a SQLAlchemy engine with custom arguments"""
        conn_url = cls.get_connection_url()
        to_return = create_engine(conn_url, **kwargs)
        return to_return

    @classmethod
    def init_db(cls, **engine_kwargs) -> None:
        """Initialize the database connection"""
        if cls.__engine is None:
            cls.__engine = cls.create_engine_with_args(**engine_kwargs)
            cls.__session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls.__engine
            )

    @classmethod
    def create_tables(cls) -> None:
        """Create all tables defined in the models"""
        # if engine is none, throw an error asking to init db first
        if cls.__engine is None:
            raise ValueError("Database engine is not initialized. Call init_db() first.")
        Base.metadata.create_all(cls.__engine)

    @classmethod
    def get_session(cls) -> Session:
        """Get a new database session"""
        if cls.__session_factory is None:
            cls.init_db()
        return cls.__session_factory()

    @classmethod
    def get_engine_name(cls) -> str:
        """
        Get the database engine name from the connection URL
        
        Returns:
            str: Database engine name (e.g., 'sqlite', 'postgresql', 'mysql')
        """
        url = cls.get_connection_url()
        return url.split('://')[0].split('+')[0]
