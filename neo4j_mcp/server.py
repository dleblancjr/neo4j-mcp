#!/usr/bin/env python3
"""
MCP server for Neo4j integration.
Uses modular architecture for better maintainability.
"""

import asyncio
import logging
import argparse
import signal  # Added for graceful SIGTERM/SIGINT handling
import os  # Added for Windows detection
import time  # Added for monotonic uptime tracking without requiring an event loop
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult
from pydantic import ValidationError  # New import for benign suppression
from anyio import BrokenResourceError  # New import for benign suppression

from .tools import get_all_tools
from .database import Neo4jOperations
from .operations import SearchOperations, EntityOperations, RelationshipOperations, ObservationOperations

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Central schema definition for runtime validation (edge MCP compliance)
TOOL_REQUIRED_ARGS: Dict[str, List[str]] = {
    "connect_neo4j": ["uri", "username", "password"],
    "run_cypher_query": ["query"],
    "find_nodes": ["name"],
    "search_nodes": ["search_string"],
    "create_entities": ["entity_type", "properties"],
    "delete_entities": ["entity_id"],
    "create_relations": ["source_id", "target_id", "relationship_type"],
    "delete_relations": ["source_id", "target_id"],
    "add_observations": ["entity_id", "observation_text"],
    "delete_observations": ["entity_id"],
    "disconnect_neo4j": [],
    "health_check": [],
    "shutdown_server": [],
}

# Unified timeout for potentially long-running tool operations (cancellation safety)
TOOL_EXECUTION_TIMEOUT_SECONDS = Neo4jOperations.DEFAULT_QUERY_TIMEOUT_SECONDS + 5

class Neo4jMCPServer:
    def __init__(self, neo4j_uri: str = None, neo4j_username: str = None, neo4j_password: str = None, stop_event: Optional[asyncio.Event] = None):
        """Initialize the Neo4j MCP Server."""
        self.server = Server("neo4j-mcp")
        self.db_operations = Neo4jOperations(neo4j_uri, neo4j_username, neo4j_password)
        self.search_operations = SearchOperations(self.db_operations)
        self.entity_operations = EntityOperations(self.db_operations)
        self.relationship_operations = RelationshipOperations(self.db_operations)
        self.observation_operations = ObservationOperations(self.db_operations)
        # Track start time for uptime reporting using monotonic clock (no event loop dependency)
        self._start_time = time.monotonic()
        # External stop event (for shutdown_server tool); create if not supplied
        self._external_stop_event = stop_event
        self.setup_handlers()
    
    @staticmethod
    def _validate_arguments(tool_name: str, arguments: Optional[Dict[str, Any]]) -> Optional[CallToolResult]:
        """Validate required arguments for a tool. Returns error CallToolResult on failure."""
        if arguments is None:
            arguments = {}
        required = TOOL_REQUIRED_ARGS.get(tool_name, [])
        missing = [r for r in required if r not in arguments or arguments[r] in (None, "")]
        if missing:
            return CallToolResult(
                content=[{"type": "text", "text": f"Missing required argument(s) for {tool_name}: {', '.join(missing)}"}],
                isError=True
            )
        return None

    def setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(tools=get_all_tools())
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls with schema validation and cancellation safety."""
            # Validate arguments against required schema first
            arg_error = self._validate_arguments(name, arguments)
            if arg_error:
                return arg_error
            try:
                # Wrap tool execution in timeout for cancellation safety (exclude trivial tools)
                long_running = name not in {"health_check", "disconnect_neo4j", "shutdown_server"}
                if long_running:
                    async with asyncio.timeout(TOOL_EXECUTION_TIMEOUT_SECONDS):
                        return await self._dispatch_tool(name, arguments)
                else:
                    return await self._dispatch_tool(name, arguments)
            except asyncio.TimeoutError:
                return CallToolResult(
                    content=[{"type": "text", "text": f"Tool '{name}' execution timed out"}],
                    isError=True
                )
            except Exception as e:
                logger.error(f"Error in tool call {name}: {e}")
                return CallToolResult(
                    content=[{"type": "text", "text": f"Error: {str(e)}"}],
                    isError=True
                )

    async def _dispatch_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Internal dispatcher separated for timeout wrapping."""
        if name == "connect_neo4j":
            return await self.connect_neo4j(arguments)
        elif name == "run_cypher_query":
            return await self.run_cypher_query(arguments)
        elif name == "find_nodes":
            return await self.search_operations.find_nodes(arguments)
        elif name == "search_nodes":
            return await self.search_operations.search_nodes(arguments)
        elif name == "create_entities":
            return await self.entity_operations.create_entities(arguments)
        elif name == "delete_entities":
            return await self.entity_operations.delete_entities(arguments)
        elif name == "create_relations":
            return await self.relationship_operations.create_relations(arguments)
        elif name == "delete_relations":
            return await self.relationship_operations.delete_relations(arguments)
        elif name == "add_observations":
            return await self.observation_operations.add_observations(arguments)
        elif name == "delete_observations":
            return await self.observation_operations.delete_observations(arguments)
        elif name == "disconnect_neo4j":
            return await self.disconnect_neo4j(arguments)
        elif name == "health_check":
            return await self.health_check(arguments)
        elif name == "shutdown_server":
            return await self.shutdown_server(arguments)
        else:
            return CallToolResult(
                content=[{"type": "text", "text": f"Unknown tool: {name}"}],
                isError=True
            )

    async def connect_neo4j(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Connect or reconnect to Neo4j applying force semantics.

        - If driver exists and force not set/False: skip reconnect.
        - If driver exists and force True: disconnect then reconnect.
        - If no driver: connect.
        """
        force = bool(arguments.get("force", False))
        # Determine if a real driver exists: attribute explicitly set and not None
        existing_driver = None
        if isinstance(getattr(self.db_operations, '__dict__', {}), dict):
            existing_driver = self.db_operations.__dict__.get('driver')
        else:  # Fallback if object lacks __dict__ (unlikely)
            try:
                existing_driver = object.__getattribute__(self.db_operations, 'driver')  # may raise
            except Exception:  # noqa: BLE001
                existing_driver = None
        if existing_driver is not None and not force:
            return CallToolResult(content=[{"type": "text", "text": "Already connected; skipping reconnect (use force=true to reconnect)."}])
        if existing_driver is not None and force:
            await self.db_operations.disconnect()
        uri = arguments["uri"]
        username = arguments["username"]
        password = arguments["password"]
        return await self.db_operations.connect(uri, username, password)

    async def manual_connect_neo4j(self, arguments: Dict[str, Any]) -> CallToolResult:  # backward compatibility for tests
        return await self.connect_neo4j(arguments)
    
    async def run_cypher_query(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Run a Cypher query (timeout handled by outer wrapper)."""
        query = arguments["query"]
        parameters = arguments.get("parameters", {})
        return await self.db_operations.run_query(query, parameters)

    async def disconnect_neo4j(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Disconnect from Neo4j database."""
        return await self.db_operations.disconnect()

    async def health_check(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Return server health status including connection state, version, sanitized URI, uptime and concurrency metrics."""
        connected = bool(self.db_operations.driver)
        # Build sanitized URI (hide credentials if embedded like neo4j://user:pass@host)
        raw_uri = getattr(self.db_operations, '_env_uri', None)
        display_uri = None
        if raw_uri:
            # Strip potential creds pattern user:pass@
            display_uri = raw_uri.split('@')[-1] if '@' in raw_uri else raw_uri
        uptime_seconds = time.monotonic() - self._start_time
        concurrency = self.db_operations.concurrency_metrics()
        status_lines = [
            f"server_name=neo4j-mcp",
            f"server_version=1.0.0",
            f"connected={connected}",
            f"neo4j_uri={(display_uri or 'unknown')}",
            f"uptime_seconds={uptime_seconds:.2f}",
            f"max_concurrency={concurrency['max_concurrency']}",
            f"active_operations={concurrency['active_operations']}",
            f"available_slots={concurrency['available_slots']}",
            f"default_query_timeout_seconds={concurrency['default_query_timeout_seconds']}",
        ]
        return CallToolResult(content=[{"type": "text", "text": "Health Check:\n" + "\n".join(status_lines)}])

    async def shutdown_server(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Request graceful server shutdown via external stop event (if available)."""
        if self._external_stop_event is None:
            return CallToolResult(content=[{"type": "text", "text": "Shutdown not supported in this context (no stop event)."}], isError=True)
        if self._external_stop_event.is_set():
            return CallToolResult(content=[{"type": "text", "text": "Shutdown already in progress."}])
        self._external_stop_event.set()
        return CallToolResult(content=[{"type": "text", "text": "Shutdown signal accepted. Server will terminate shortly."}])

# --- Cross-platform signal handling helper ---

def _install_signal_handlers(stop_event: asyncio.Event, loop: asyncio.AbstractEventLoop):
    """Install signal handlers for POSIX & provide fallbacks for Windows.

    Attempts loop.add_signal_handler first; if unavailable (NotImplementedError / RuntimeError),
    falls back to signal.signal (works on main thread). On Windows adds SIGBREAK if present.
    """
    def _request_shutdown(sig_name: str):
        if not stop_event.is_set():
            logger.info(f"Received {sig_name}. Initiating graceful shutdown...")
            stop_event.set()

    potential_signals = [signal.SIGINT]
    # SIGTERM may not exist in very old/embedded envs
    if hasattr(signal, "SIGTERM"):
        potential_signals.append(signal.SIGTERM)
    # Windows specific CTRL+BREAK
    if os.name == "nt" and hasattr(signal, "SIGBREAK"):
        potential_signals.append(signal.SIGBREAK)

    registered = []
    for sig in potential_signals:
        try:
            loop.add_signal_handler(sig, _request_shutdown, sig.name)
            registered.append(sig.name)
        except (NotImplementedError, RuntimeError):  # RuntimeError if not main thread
            try:
                # Fallback: synchronous handler sets the event
                def _handler(signum, frame, name=sig.name):  # noqa: ANN001
                    _request_shutdown(name)
                signal.signal(sig, _handler)
                registered.append(sig.name + ":fallback")
            except Exception:  # noqa: BLE001
                logger.debug("Could not register handler for signal %s", sig)
                continue
    if registered:
        logger.debug("Registered signal handlers: %s", ", ".join(registered))
    else:
        logger.debug("No signal handlers registered (environment limitation)")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Neo4j MCP Server")
    parser.add_argument("--neo4j-uri", 
                       help="Neo4j connection URI (e.g., neo4j://localhost:7687)")
    parser.add_argument("--neo4j-username", 
                       help="Neo4j username")
    parser.add_argument("--neo4j-password", 
                       help="Neo4j password")
    parser.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    return parser.parse_args()

async def main():
    """Main entry point with graceful shutdown handling including SIGTERM/SIGINT (cross-platform)."""
    args = parse_arguments()    
    # Adjust log level early (overwriting initial basicConfig if needed)
    logging.getLogger().setLevel(getattr(logging, getattr(args, 'log_level', 'INFO').upper(), logging.INFO))
    if args.neo4j_uri is None:
        # IMPORTANT: Avoid printing to stdout before JSON-RPC handshake.
        # Use logger so output goes to stderr and doesn't corrupt protocol.
        logger.info("Loading Neo4j connection parameters from environment (.env if present)")
        load_dotenv(override=True)
        args.neo4j_uri = os.getenv('NEO4J_URI')
        args.neo4j_username = os.getenv('NEO4J_USERNAME')
        args.neo4j_password = os.getenv('NEO4J_PASSWORD')    

    stop_event = asyncio.Event()

    neo4j_server = Neo4jMCPServer(
        neo4j_uri=args.neo4j_uri,
        neo4j_username=args.neo4j_username,
        neo4j_password=args.neo4j_password,
        stop_event=stop_event
    )

    # --- New: perform eager connection so user gets success/failure feedback immediately ---
    if all([args.neo4j_uri, args.neo4j_username, args.neo4j_password]):
        if neo4j_server.db_operations.driver is None:  # only if not already connected
            connect_result = await neo4j_server.db_operations.connect(
                args.neo4j_uri, args.neo4j_username, args.neo4j_password
            )
            if connect_result.isError:
                logger.warning("Initial Neo4j connection attempt failed: %s", connect_result.content[0].text)
            else:
                # Disable further lazy auto-connect attempts
                neo4j_server.db_operations._auto_connect_pending = False
        else:
            logger.debug("Neo4j driver already initialized before eager connect.")
    else:
        logger.info("Neo4j connection parameters not fully provided; awaiting manual connect tool call.")

    loop = asyncio.get_running_loop()
    _install_signal_handlers(stop_event, loop)
    
    try:
        # NOTE: Do not write to stdout directly (only JSON-RPC). All diagnostics must go via logging (stderr).
        async with stdio_server() as (read_stream, write_stream):
            server_task = asyncio.create_task(
                neo4j_server.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="neo4j-mcp",
                        server_version="1.0.0",
                        capabilities=neo4j_server.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
            )

            # Wait for either the server task to finish or a shutdown signal
            stop_task = asyncio.create_task(stop_event.wait())
            done, pending = await asyncio.wait({server_task, stop_task}, return_when=asyncio.FIRST_COMPLETED)

            if stop_task in done and not server_task.done():
                # Gracefully cancel server task
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    logger.debug("Server task cancelled during shutdown.")
    except BaseExceptionGroup as eg:  # Python 3.11+ aggregated exceptions (e.g., from anyio TaskGroup)
        # Suppress benign termination / parse noise when no proper JSON-RPC client is attached.
        benign = (ValidationError, BrokenResourceError)
        if all(isinstance(e, benign) for e in eg.exceptions):
            logger.info("Suppressing benign input termination errors (%d).", len(eg.exceptions))
        else:
            logger.error("Unhandled server error group: %s", eg)
            raise
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down gracefully...")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Unhandled server error: {e}")
        raise
    finally:
        # Attempt clean disconnect
        try:
            await neo4j_server.db_operations.disconnect()
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Error during disconnect: {e}")
        logger.info("Server shutdown complete.")

def run_main():
    """Synchronous entry point for the console script."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Extra safeguard if interrupt happens outside main loop phases
        logger.info("Interrupted. Exiting.")

if __name__ == "__main__":
    run_main()