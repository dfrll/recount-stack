#! /usr/bin/env python3
import os
import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


def get_db_connection():
    """Get a database connection"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
    )


@contextmanager
def db_transaction():
    """Context manager for database transactions with RealDictCursor"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit()  # Commit after the with block
    except Exception as e:
        conn.rollback()
        logger.error("Database transaction failed: %s", e)
        raise
    finally:
        conn.close()
