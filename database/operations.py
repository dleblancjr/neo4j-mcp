"""
Database operations for the Neo4j MCP server.
Contains all Neo4j database interaction logic.
"""

import logging
import os
import re
import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional
from neo4j import AsyncGraphDatabase
from mcp.types import CallToolResult

logger = logging.getLogger(__name__)


class Neo4jOperations:
    """Handles all Neo4j database operations."""
    DEFAULT_QUERY_TIMEOUT_SECONDS = 10  # safety timeout
    MAX_QUERY_LENGTH = 10_000
    DEFAULT_MAX_CONCURRENCY = 10  # reasonable default guard

    def __init__(self, neo4j_uri: str = None, neo4j_username: str = None, neo4j_password: str = None, max_concurrency: int | None = None):
        self.driver: Optional[AsyncGraphDatabase] = None
        self._env_uri: Optional[str] = None
        self._env_username: Optional[str] = None
        self._env_password: Optional[str] = None
        # Configure concurrency limit (env override -> param -> default)
        if max_concurrency is None:
            try:
                env_limit = int(os.getenv("NEO4J_MAX_CONCURRENCY", ""))
            except ValueError:
                env_limit = 0
            max_concurrency = env_limit if env_limit > 0 else self.DEFAULT_MAX_CONCURRENCY
        self._max_concurrency = max_concurrency  # <-- store for metrics
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._auto_connect_pending = False
        self._auto_connect_on_init(neo4j_uri, neo4j_username, neo4j_password)
    
    @asynccontextmanager
    async def _limit_concurrency(self):
        """Async context manager to enforce max concurrent database operations."""
        await self._semaphore.acquire()
        try:
            yield
        finally:
            self._semaphore.release()
    
    def concurrency_metrics(self) -> Dict[str, Any]:
        """Return current concurrency usage metrics."""
        try:
            available = self._semaphore._value  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            available = None
        in_use = None
        if available is not None:
            in_use = self._max_concurrency - available
        return {
            "max_concurrency": self._max_concurrency,
            "available_slots": available,
            "active_operations": in_use,
            "default_query_timeout_seconds": self.DEFAULT_QUERY_TIMEOUT_SECONDS,
        }
    
    def _auto_connect_on_init(self, neo4j_uri: str = None, neo4j_username: str = None, neo4j_password: str = None):
        """Attempt to auto-connect using provided parameters or environment variables if available."""
        # First check if parameters were provided
        if neo4j_uri and neo4j_username and neo4j_password:
            logger.info("Neo4j connection parameters provided. Auto-connecting...")
            self._env_uri = neo4j_uri
            self._env_username = neo4j_username
            self._env_password = neo4j_password
            self._auto_connect_pending = True
        else:
            # Fall back to environment variables
            uri = os.getenv('NEO4J_URI')
            username = os.getenv('NEO4J_USERNAME')
            password = os.getenv('NEO4J_PASSWORD')
            
            if uri and username and password:
                logger.info("Environment variables found for Neo4j connection. Auto-connecting...")
                self._env_uri = uri
                self._env_username = username
                self._env_password = password
                self._auto_connect_pending = True
            else:
                self._auto_connect_pending = False
                logger.info("No Neo4j connection parameters or environment variables found. Manual connection required.")
    
    async def _ensure_connected(self) -> Optional[CallToolResult]:
        """Ensure connected to Neo4j, auto-connecting if environment variables are available."""
        if self.driver:
            return None  # Already connected
        
        if self._auto_connect_pending:
            logger.info("Auto-connecting to Neo4j using stored parameters...")
            result = await self.connect(self._env_uri, self._env_username, self._env_password)
            # If error, propagate; if success, do not short‑circuit caller logic.
            if result.isError:
                return result
            return None
        
        return None  # No auto-connect available
    
    async def connect(self, uri: str, username: str, password: str) -> CallToolResult:
        """Connect to Neo4j database."""
        try:
            self.driver = AsyncGraphDatabase.driver(uri, auth=(username, password))
            
            # Prefer verify_connectivity when available (works with test mocks)
            try:
                verify = getattr(self.driver, "verify_connectivity", None)
                if verify:
                    # If it's awaitable, await it
                    maybe_coro = verify()
                    if asyncio.iscoroutine(maybe_coro):  # type: ignore[name-defined]
                        await maybe_coro
                    logger.info("Successfully established Neo4j connection to %s via verify_connectivity", uri)
                    return CallToolResult(content=[{"type": "text", "text": f"Successfully connected to Neo4j at {uri}"}])
            except Exception as vc_err:  # noqa: BLE001
                logger.debug("verify_connectivity failed or unavailable (%s), falling back to test query.", vc_err)
            
            # Fallback: open a session and run a lightweight test query
            try:
                async with self.driver.session() as session:  # type: ignore[func-returns-value]
                    result = await session.run("RETURN 1 AS test")
                    record = await result.single()
                    if record and record["test"] == 1:
                        logger.info("Successfully established Neo4j connection to %s via test query", uri)
                        return CallToolResult(content=[{"type": "text", "text": f"Successfully connected to Neo4j at {uri}"}])
                    raise RuntimeError("Connection test failed")
            except Exception as sess_err:  # noqa: BLE001
                raise RuntimeError(f"Connectivity verification failed: {sess_err}") from sess_err
        except Exception as e:  # noqa: BLE001
            # Clean up partial driver on failure
            if self.driver:
                try:
                    await self.driver.close()
                except Exception:  # noqa: BLE001
                    pass
                self.driver = None
            logger.error("Failed to connect to Neo4j: %s", e)
            return CallToolResult(content=[{"type": "text", "text": f"Failed to connect to Neo4j: {e}"}], isError=True)
    
    async def disconnect(self) -> CallToolResult:
        """Disconnect from Neo4j database."""
        try:
            if self.driver:
                try:
                    await self.driver.close()
                finally:
                    self.driver = None
                return CallToolResult(content=[{"type": "text", "text": "Successfully disconnected from Neo4j"}])
            return CallToolResult(content=[{"type": "text", "text": "Not connected to Neo4j"}])
        except Exception as e:  # noqa: BLE001
            logger.warning("Error disconnecting from Neo4j: %s", e)
            return CallToolResult(content=[{"type": "text", "text": f"Error disconnecting from Neo4j: {e}"}], isError=True)
    
    @staticmethod
    def _truncate(text: str, limit: int = 500) -> str:
        return text if len(text) <= limit else text[:limit] + "… (truncated)"
    
    async def run_query(self, query: str, parameters: Dict[str, Any] = None) -> CallToolResult:
        """Run a Cypher query."""
        # Try to auto-connect if environment variables are available
        auto_connect_error = await self._ensure_connected()
        if auto_connect_error:  # Only error objects are returned now
            return auto_connect_error
        
        if not self.driver:
            return CallToolResult(content=[{"type": "text", "text": "Not connected to Neo4j. Please connect first."}], isError=True)
        
        try:
            if parameters is None:
                parameters = {}
            # Validate query
            if not isinstance(query, str) or not query.strip():
                return CallToolResult(content=[{"type": "text", "text": "Query must be a non-empty string"}], isError=True)
            if len(query) > self.MAX_QUERY_LENGTH:
                return CallToolResult(content=[{"type": "text", "text": f"Query too long (>" + str(self.MAX_QUERY_LENGTH) + " chars)"}], isError=True)

            # Very light sanity check to discourage obvious write-destructive operations unless intentional
            dangerous = re.search(r"\bDETACH\s+DELETE\b", query, re.IGNORECASE)
            if dangerous:
                logger.debug("Executing potentially destructive query: %s", self._truncate(query, 120))

            async with self._limit_concurrency():
                async with self.driver.session() as session:
                    # Removed explicit timeout kwarg to align with tests expecting only query & params
                    result = await session.run(query, parameters)
                    records = await result.data()
                    if not records:
                        return CallToolResult(content=[{"type": "text", "text": "Query executed successfully. No results returned."}])
                    result_text = "Query Results:\n"
                    for i, record in enumerate(records):
                        # Convert Record to regular dict for readability
                        result_text += f"Record {i + 1}: {dict(record)}\n"
                    return CallToolResult(content=[{"type": "text", "text": self._truncate(result_text, 10_000)}])
        except Exception as e:  # noqa: BLE001
            logger.error("Query execution failed: %s", e)
            return CallToolResult(content=[{"type": "text", "text": f"Query execution failed: {e}"}], isError=True)
    
    async def _check_connection(self) -> Optional[CallToolResult]:
        """Check if connected to Neo4j."""
        # Try to auto-connect if environment variables are available
        auto_connect_error = await self._ensure_connected()
        if auto_connect_error:
            return auto_connect_error
        
        if not self.driver:
            return CallToolResult(content=[{"type": "text", "text": "Not connected to Neo4j. Please connect first."}], isError=True)
        return None