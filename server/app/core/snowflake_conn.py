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


def execute_query_with_in_clause(query_template: str, ids: list, param_name: str = "ids", other_params: dict = None):
    """
    Execute a query with IN clause safely.
    
    Snowflake requires special handling for IN clauses with parameterized queries.
    This function generates safe SQL with individual placeholders for each ID.
    
    Args:
        query_template: SQL query with {placeholders} for IN clause
        ids: List of IDs to include in IN clause
        param_name: Name of the parameter in the query
        other_params: Other parameters for the query
    
    Returns:
        Query results
    
    Example:
        query = "SELECT * FROM table WHERE id IN ({placeholders})"
        results = execute_query_with_in_clause(query, ['id1', 'id2'], other_params={'user_id': 'user123'})
    """
    if not ids:
        return []
    
    # Create placeholders like: %(id_0)s, %(id_1)s, %(id_2)s
    placeholders = ", ".join([f"%({param_name}_{i})s" for i in range(len(ids))])
    
    # Build the final query by replacing {placeholders}
    final_query = query_template.replace("{placeholders}", placeholders)
    
    # Build parameters dictionary
    params = other_params.copy() if other_params else {}
    for i, id_val in enumerate(ids):
        params[f"{param_name}_{i}"] = id_val
    
    return execute_query(final_query, params)


def close_connection():
    """Close the Snowflake connection."""
    global _connection
    if _connection and not _connection.is_closed():
        _connection.close()
        logger.info("Snowflake connection closed")
        _connection = None