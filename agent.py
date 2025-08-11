#!/usr/bin/env python3
"""Local test agent: start local neo4j-mcp server (same workspace) and list tools.

Simplified for local development ONLY:
    * Always launches the server using current interpreter: python -m neo4j_mcp.server
    * Forwards optional Neo4j connection parameters via CLI or environment/.env
    * Lists tools and prints them (text or JSON)
    * Supports debug frame tracing (--trace-frames)

Environment variables honored (and NOT overridden): NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD.
You can also supply them via CLI flags here which are passed to the server process.
"""
from __future__ import annotations

import asyncio
import os
import sys
import json
import argparse
import logging
from typing import List

# Lazy import so we can print a helpful message if missing
try:  # ...existing code...
    from mcp.client.stdio import stdio_client, StdioServerParameters  # type: ignore
    from mcp.client.session import ClientSession  # type: ignore
except Exception as _imp_err:  # noqa: BLE001
    print("[error] Missing 'mcp' package. Install with: pip install mcp", file=sys.stderr)
    raise

DEFAULT_TIMEOUT = 15.0
logger = logging.getLogger("agent")

# --- .env loading ---

def _load_local_env() -> None:
    """Load a .env file that sits next to this script (non-fatal if absent).

    Precedence rules:
      * Existing environment variables are NOT overridden.
      * If python-dotenv is installed, use it (it handles quoting, exports, etc.).
      * Otherwise do a minimal manual parse: KEY=VALUE, ignore blanks & lines starting with '#'.
    """
    script_dir = os.path.abspath(os.path.dirname(__file__))
    env_path = os.path.join(script_dir, ".env")
    if not os.path.isfile(env_path):
        logger.debug("No .env file found at %s", env_path)
        return
    # Try python-dotenv first
    try:  # ...existing code...
        from dotenv import load_dotenv  # type: ignore
        loaded = load_dotenv(env_path, override=False)
        if loaded:
            logger.debug("Loaded environment variables from %s via python-dotenv", env_path)
        else:
            logger.debug("python-dotenv did not load any variables from %s (maybe all already set)", env_path)
        return
    except Exception:  # noqa: BLE001
        logger.debug("python-dotenv not available; falling back to manual .env parsing")
    # Fallback manual parse
    added = 0
    try:
        with open(env_path, "r", encoding="utf-8") as fh:  # noqa: PTH123
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                # Strip optional quotes
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
                    added += 1
        logger.debug("Loaded %d env vars from %s (manual parser)", added, env_path)
    except Exception as e:  # noqa: BLE001
        logger.warning("Failed to parse .env file %s: %s", env_path, e)

# --- CLI Parsing ---

def parse_args():  # noqa: D401
    p = argparse.ArgumentParser(description="List tools from local neo4j-mcp server")
    p.add_argument("--json", action="store_true", help="Output tools as JSON array instead of text")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Timeout seconds for initialize+list")
    p.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    p.add_argument("--trace-frames", action="store_true", help="Log raw JSON-RPC frames sent/received by client (debug)")
    p.add_argument("--protocol-version", default="2024-11-05", help="Protocol version string for initialize")
    p.add_argument("--direct", action="store_true", help="Bypass MCP and list tools directly (debug/dev mode)")
    # Optional: allow supplying neo4j params; if omitted server will pull from env/.env
    p.add_argument("--neo4j-uri", help="Neo4j URI (overrides env)")
    p.add_argument("--neo4j-username", help="Neo4j username (overrides env)")
    p.add_argument("--neo4j-password", help="Neo4j password (overrides env)")
    return p.parse_args()

# --- Core logic ---
async def list_tools(server_args: List[str], timeout: float, trace_frames: bool=False, protocol_version: str = "2024-11-05") -> List:
    # Always launch local server using current interpreter
    command = sys.executable
    if not os.path.exists(command):  # paranoid check
        raise RuntimeError("Python interpreter not found for launching server")
    # Build environment (inherit; don't override existing NEO4J_* values)
    params = StdioServerParameters(command=command, args=server_args, env=os.environ.copy())
    logger.debug("Launching local server: %s %s", command, " ".join(server_args))
    async with stdio_client(params) as (read_stream, write_stream):  # type: ignore
        if trace_frames:
            # Wrap send/receive to log raw protocol messages
            try:
                original_receive = read_stream.receive  # type: ignore[attr-defined]
                async def debug_receive():  # type: ignore[no-redef]
                    msg = await original_receive()
                    logger.debug("CLIENT RAW INCOMING FRAME: %r", msg)
                    return msg
                read_stream.receive = debug_receive  # type: ignore[attr-defined]
            except Exception as e:  # noqa: BLE001
                logger.debug("Could not wrap read_stream.receive: %s", e)
            try:
                original_send = write_stream.send  # type: ignore[attr-defined]
                async def debug_send(msg):  # type: ignore[no-redef]
                    logger.debug("CLIENT RAW OUTGOING FRAME: %r", msg)
                    return await original_send(msg)
                write_stream.send = debug_send  # type: ignore[attr-defined]
            except Exception as e:  # noqa: BLE001
                logger.debug("Could not wrap write_stream.send: %s", e)
        # Use ClientSession as async context manager so internal tasks are managed properly
        async with ClientSession(read_stream=read_stream, write_stream=write_stream) as session:  # type: ignore
            try:
                async with asyncio.timeout(timeout):
                    logger.debug("Initializing MCP client session (timeout=%.2fs)...", timeout)
                    await asyncio.sleep(0.02)  # tiny delay to let server start
                    import inspect
                    init_sig = None
                    try:
                        init_sig = inspect.signature(session.initialize)  # type: ignore[arg-type]
                    except Exception:  # noqa: BLE001
                        pass
                    use_kw = False
                    if init_sig:
                        for p in init_sig.parameters.values():
                            if p.name in ("protocol_version", "protocolVersion"):
                                use_kw = True
                                break
                    if use_kw:
                        logger.debug("Passing protocol_version kw (%s) to initialize", protocol_version)
                        await session.initialize(protocol_version=protocol_version)  # type: ignore[arg-type]
                    else:
                        logger.debug("initialize() signature has no protocol_version kw; calling without it")
                        await session.initialize()
                    logger.debug("Initialization completed; sending list_tools request...")
                    try:
                        tool_result = await session.list_tools()
                    except BaseException as e:  # noqa: BLE001
                        if isinstance(e, BaseExceptionGroup):
                            logger.error("list_tools raised BaseExceptionGroup with %d sub-exceptions", len(e.exceptions))
                            for idx, sub in enumerate(e.exceptions):
                                logger.error("  [%d] %s: %s", idx, type(sub).__name__, sub, exc_info=sub)
                        else:
                            logger.error("list_tools raised %s: %s", type(e).__name__, e, exc_info=e)
                        raise
                    logger.debug("Received %d tools", len(getattr(tool_result, 'tools', []) or []))
                    return tool_result.tools
            except (asyncio.TimeoutError, TimeoutError) as e:  # noqa: PERF203
                raise RuntimeError("Operation timed out (initialize or list_tools)") from e
            except Exception as e:  # noqa: BLE001
                logger.error("Failed during list_tools sequence: %s", e)
                raise

# --- Output helpers ---

def tools_to_text(tools: List) -> str:
    if not tools:
        return "(No tools returned)"
    lines = ["=== neo4j-mcp Tools ==="]
    for t in tools:
        name = getattr(t, "name", "<unknown>")
        desc = getattr(t, "description", "") or ""
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)

def tools_to_json(tools: List) -> str:
    return json.dumps([
        {"name": getattr(t, "name", None), "description": getattr(t, "description", None)} for t in tools
    ], ensure_ascii=False, indent=2)

# --- Main ---
async def _main_async():  # noqa: D401
    _load_local_env()
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger.debug("Parsed args: %s", args)

    if args.direct:
        # Direct import path (bypass MCP) for quick local inspection
        try:
            from neo4j_mcp.tools import get_all_tools  # type: ignore
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to import tools directly: %s", e)
            sys.exit(1)
        tools = get_all_tools()
        if args.json:
            print(tools_to_json(tools))
        else:
            print(tools_to_text(tools))
        return

    # Compose server arguments (module invocation + optional neo4j creds)
    server_args = ["-m", "neo4j_mcp.server"]
    if args.neo4j_uri:
        server_args += ["--neo4j-uri", args.neo4j_uri]
    if args.neo4j_username:
        server_args += ["--neo4j-username", args.neo4j_username]
    if args.neo4j_password:
        server_args += ["--neo4j-password", args.neo4j_password]
    server_args += ["--log-level", args.log_level]

    logger.debug("Server invocation args: %s", " ".join(server_args))
    tools = await list_tools(
        server_args,
        args.timeout,
        trace_frames=args.trace_frames,
        protocol_version=args.protocol_version,
    )
    if args.json:
        print(tools_to_json(tools))
    else:
        print(tools_to_text(tools))

def main():  # noqa: D401
    try:
        asyncio.run(_main_async())
    except KeyboardInterrupt:
        print("Interrupted.")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":  # pragma: no cover
    main()
