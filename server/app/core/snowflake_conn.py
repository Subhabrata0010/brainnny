"""
Snowflake database connection management.
Provides connection pooling and query execution helpers.
"""

import logging
import snowflake.connector
from snowflake.connector import SnowflakeConnection
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global connection instance
_connection: SnowflakeConnection = None


def get_snowflake_connection() -> SnowflakeConnection:
    """
    Get or create a Snowflake connection.
    Auto-reconnects if connection is closed.
    
    Returns:
        Active Snowflake connection
    """
    global _connection
    
    if _connection is None or _connection.is_closed():
        logger.info("Creating new Snowflake connection...")
        _connection = snowflake.connector.connect(
            user=settings.SNOWFLAKE_USER,
            password=settings.SNOWFLAKE_PASSWORD,
            account=settings.SNOWFLAKE_ACCOUNT,
            warehouse=settings.SNOWFLAKE_WAREHOUSE,
            database=settings.SNOWFLAKE_DATABASE,
            schema=settings.SNOWFLAKE_SCHEMA
        )
        logger.info("Snowflake connection established")
    
    return _connection


def execute_query(query: str, params: dict = None, fetch: bool = True):
    """
    Execute a Snowflake query with optional parameters.
    
    Args:
        query: SQL query string
        params: Optional query parameters
        fetch: Whether to fetch and return results
    
    Returns:
        Query results if fetch=True, else None
    """
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            return cursor.fetchall()
        else:
            return None
    finally:
        cursor.close()


def close_connection():
    """Close the Snowflake connection."""
    global _connection
    if _connection and not _connection.is_closed():
        _connection.close()
        logger.info("Snowflake connection closed")
        _connection = None