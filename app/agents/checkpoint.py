"""LangGraph Postgres checkpointer (conversation memory)."""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

load_dotenv()

_pool: Optional[ConnectionPool] = None
_checkpointer: Optional[PostgresSaver] = None


def checkpoint_conninfo() -> str:
    """Convert SQLAlchemy DATABASE_URL to a psycopg conninfo string."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def init_checkpointer() -> PostgresSaver:
    """Create the connection pool, run checkpoint migrations, return saver."""
    global _pool, _checkpointer
    if _checkpointer is not None:
        return _checkpointer

    _pool = ConnectionPool(
        conninfo=checkpoint_conninfo(),
        max_size=10,
        kwargs={"autocommit": True, "prepare_threshold": 0},
    )
    _checkpointer = PostgresSaver(_pool)
    _checkpointer.setup()
    return _checkpointer


def get_checkpointer() -> PostgresSaver:
    if _checkpointer is None:
        raise RuntimeError("Checkpointer not initialized. Call init_checkpointer() on startup.")
    return _checkpointer


def close_checkpointer() -> None:
    global _pool, _checkpointer
    if _pool is not None:
        _pool.close()
    _pool = None
    _checkpointer = None
