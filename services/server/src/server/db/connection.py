#! /usr/bin/env python3
import os
import psycopg2
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


def get_db_connection():
    """Get a database connection"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432),
    )


@contextmanager
def db_transaction():
    """Context manager for database transactions with RealDictCursor"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield conn, cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        conn.close()
