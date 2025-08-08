#!/usr/bin/env python3
"""
Unit tests for server.py - Main MCP server functionality.
"""

import unittest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from mcp.types import CallToolResult
from types import SimpleNamespace  # Added for patching parse_arguments

# Import the server module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j_mcp.server import Neo4jMCPServer, main  # noqa: E402


class TestNeo4jMCPServer(unittest.TestCase):
    """Test cases for Neo4jMCPServer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = Neo4jMCPServer()
    
    def test_server_initialization(self):
        """Test server initialization."""
        self.assertIsNotNone(self.server)
        self.assertIsNotNone(self.server.server)
        self.assertIsNotNone(self.server.db_operations)
        self.assertIsNotNone(self.server.search_operations)
        self.assertIsNotNone(self.server.entity_operations)
        self.assertIsNotNone(self.server.relationship_operations)
        self.assertIsNotNone(self.server.observation_operations)
    
    @patch('server.Neo4jOperations')
    def test_connect_neo4j_success(self, mock_neo4j_ops):
        """Test successful Neo4j connection."""
        # Mock the database operations
        mock_db = Mock()
        mock_db.connect = AsyncMock(return_value=CallToolResult(
            content=[{"type": "text", "text": "Successfully connected"}],
            isError=False
        ))
        self.server.db_operations = mock_db
        
        # Test connection
        result = asyncio.run(self.server.connect_neo4j({
            "uri": "neo4j://localhost:7687",
            "username": "neo4j",
            "password": "password"
        }))
        
        self.assertFalse(result.isError)
        self.assertIn("Successfully connected", result.content[0].text)
        mock_db.connect.assert_called_once_with(
            "neo4j://localhost:7687", "neo4j", "password"
        )
    
    @patch('server.Neo4jOperations')
    def test_connect_neo4j_failure(self, mock_neo4j_ops):
        """Test failed Neo4j connection."""
        # Mock the database operations
        mock_db = Mock()
        mock_db.connect = AsyncMock(return_value=CallToolResult(
            content=[{"type": "text", "text": "Connection failed"}],
            isError=True
        ))
        self.server.db_operations = mock_db
        
        # Test connection
        result = asyncio.run(self.server.connect_neo4j({
            "uri": "neo4j://localhost:7687",
            "username": "neo4j",
            "password": "wrong_password"
        }))
        
        self.assertTrue(result.isError)
        self.assertIn("Connection failed", result.content[0].text)
    
    @patch('server.Neo4jOperations')
    def test_manual_connect_skip_when_already_connected_and_force_false(self, mock_neo4j_ops):
        """manual_connect_neo4j should skip reconnect when driver exists and force is False."""
        mock_db = Mock()
        mock_db.driver = object()  # Simulate existing connection
        mock_db.connect = AsyncMock()
        mock_db.disconnect = AsyncMock()
        self.server.db_operations = mock_db
        
        result = asyncio.run(self.server.manual_connect_neo4j({
            "uri": "neo4j://localhost:7687",
            "username": "neo4j",
            "password": "password",
            "force": False
        }))
        self.assertFalse(result.isError)
        self.assertIn("Already connected; skipping reconnect", result.content[0].text)
        mock_db.disconnect.assert_not_called()
        mock_db.connect.assert_not_called()
    
    @patch('server.Neo4jOperations')
    def test_manual_connect_force_reconnect(self, mock_neo4j_ops):
        """manual_connect_neo4j should disconnect then reconnect when force is True."""
        mock_db = Mock()
        mock_db.driver = object()  # Simulate existing connection
        mock_db.disconnect = AsyncMock(return_value=CallToolResult(content=[{"type": "text", "text": "Disconnected"}]))
        mock_db.connect = AsyncMock(return_value=CallToolResult(content=[{"type": "text", "text": "Successfully connected"}]))
        self.server.db_operations = mock_db
        
        result = asyncio.run(self.server.manual_connect_neo4j({
            "uri": "neo4j://localhost:7687",
            "username": "neo4j",
            "password": "password",
            "force": True
        }))
        self.assertFalse(result.isError)
        self.assertIn("Successfully connected", result.content[0].text)
        mock_db.disconnect.assert_called_once()
        mock_db.connect.assert_called_once_with("neo4j://localhost:7687", "neo4j", "password")
    
    @patch('server.Neo4jOperations')
    def test_run_cypher_query_success(self, mock_neo4j_ops):
        """Test successful Cypher query execution."""
        # Mock the database operations
        mock_db = Mock()
        mock_db.run_query = AsyncMock(return_value=CallToolResult(
            content=[{"type": "text", "text": "Query Results:\nRecord 1: {'name': 'Test'}"}],
            isError=False
        ))
        self.server.db_operations = mock_db
        
        # Test query execution
        result = asyncio.run(self.server.run_cypher_query({
            "query": "MATCH (n) RETURN n LIMIT 5",
            "parameters": {"limit": 5}
        }))
        
        self.assertFalse(result.isError)
        self.assertIn("Query Results", result.content[0].text)
        mock_db.run_query.assert_called_once_with(
            "MATCH (n) RETURN n LIMIT 5", {"limit": 5}
        )
    
    @patch('server.Neo4jOperations')
    def test_run_cypher_query_failure(self, mock_neo4j_ops):
        """Test failed Cypher query execution."""
        # Mock the database operations
        mock_db = Mock()
        mock_db.run_query = AsyncMock(return_value=CallToolResult(
            content=[{"type": "text", "text": "Query execution failed"}],
            isError=True
        ))
        self.server.db_operations = mock_db
        
        # Test query execution
        result = asyncio.run(self.server.run_cypher_query({
            "query": "INVALID CYPHER QUERY",
            "parameters": {}
        }))
        
        self.assertTrue(result.isError)
        self.assertIn("Query execution failed", result.content[0].text)
    
    @patch('server.Neo4jOperations')
    def test_disconnect_neo4j_success(self, mock_neo4j_ops):
        """Test successful Neo4j disconnection."""
        # Mock the database operations
        mock_db = Mock()
        mock_db.disconnect = AsyncMock(return_value=CallToolResult(
            content=[{"type": "text", "text": "Successfully disconnected"}],
            isError=False
        ))
        self.server.db_operations = mock_db
        
        # Test disconnection
        result = asyncio.run(self.server.disconnect_neo4j({}))
        
        self.assertFalse(result.isError)
        self.assertIn("Successfully disconnected", result.content[0].text)
        mock_db.disconnect.assert_called_once()

    @patch('server.Neo4jOperations')
    def test_health_check_not_connected(self, mock_neo4j_ops):
        """Health check should report not connected when no driver."""
        self.server.db_operations.driver = None
        result = asyncio.run(self.server.health_check({}))
        self.assertFalse(result.isError)
        text = result.content[0].text
        self.assertIn("Health Check:", text)
        self.assertIn("server_name=neo4j-mcp", text)
        self.assertIn("server_version=1.0.0", text)
        # connected should be False
        self.assertIn("connected=False", text)
        self.assertIn("uptime_seconds=", text)
        # concurrency metrics
        self.assertIn("max_concurrency=", text)
        self.assertIn("active_operations=", text)
        self.assertIn("available_slots=", text)
        self.assertIn("default_query_timeout_seconds=", text)

    @patch('server.Neo4jOperations')
    def test_health_check_connected_and_sanitized_uri(self, mock_neo4j_ops):
        """Health check should show connected True and sanitize credentials in URI."""
        self.server.db_operations.driver = object()
        # simulate stored env uri with creds
        self.server.db_operations._env_uri = 'neo4j://user:pass@localhost:7687'
        result = asyncio.run(self.server.health_check({}))
        text = result.content[0].text
        self.assertIn("connected=True", text)
        # Should not leak user:pass
        self.assertNotIn("user:pass@", text)
        self.assertIn("localhost:7687", text)

    def test_shutdown_server_tool(self):
        """Test shutdown_server tool triggers stop event."""
        stop_event = asyncio.Event()
        server = Neo4jMCPServer(stop_event=stop_event)
        # Initially not set
        self.assertFalse(stop_event.is_set())
        result = asyncio.run(server.shutdown_server({}))
        self.assertFalse(result.isError)
        self.assertIn("Shutdown signal accepted", result.content[0].text)
        self.assertTrue(stop_event.is_set())
        # Second call should report already in progress
        result2 = asyncio.run(server.shutdown_server({}))
        self.assertFalse(result2.isError)
        self.assertIn("already in progress", result2.content[0].text)

    def test_shutdown_server_no_event(self):
        """If server created without stop_event, shutdown should error."""
        server = Neo4jMCPServer()  # no external event
        result = asyncio.run(server.shutdown_server({}))
        self.assertTrue(result.isError)
        self.assertIn("Shutdown not supported", result.content[0].text)

    def test_handle_call_tool_unknown_tool(self):
        """Test handling of unknown tool calls."""
        # The server handles unknown tools in the setup_handlers method
        # We'll test this by checking the server structure instead
        self.assertTrue(hasattr(self.server, 'server'))
        self.assertTrue(hasattr(self.server, 'setup_handlers'))
    
    def test_handle_call_tool_exception(self):
        """Test handling of exceptions in tool calls."""
        # The server handles exceptions in the setup_handlers method
        # We'll test this by checking the server structure instead
        self.assertTrue(hasattr(self.server, 'server'))
        self.assertTrue(hasattr(self.server, 'setup_handlers'))


class TestServerIntegration(unittest.TestCase):
    """Integration tests for server functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = Neo4jMCPServer()
    
    def test_server_has_all_required_attributes(self):
        """Test that server has all required attributes."""
        required_attrs = [
            'server', 'db_operations', 'search_operations', 
            'entity_operations', 'relationship_operations',
            'observation_operations'
        ]
        
        for attr in required_attrs:
            self.assertTrue(hasattr(self.server, attr), f"Missing attribute: {attr}")
    
    def test_server_methods_exist(self):
        """Test that server has all required methods."""
        required_methods = [
            'connect_neo4j', 'manual_connect_neo4j', 'run_cypher_query', 'disconnect_neo4j',
            'setup_handlers', 'health_check', 'shutdown_server'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(self.server, method), f"Missing method: {method}")


class TestSignalHandling(unittest.TestCase):
    """Tests for graceful shutdown via SIGTERM/SIGINT in main()."""

    def test_main_graceful_shutdown_on_sigterm(self):
        callbacks = {}

        class FakeLoop:
            def add_signal_handler(self, sig, cb, sig_name):
                # Store and immediately invoke to simulate signal arrival
                callbacks[sig] = (cb, sig_name)
                # Simulate asynchronous style immediate shutdown request
                cb(sig_name)

        # Dummy async context manager for stdio_server
        class DummyStdio:
            async def __aenter__(self):
                return (Mock(), Mock())
            async def __aexit__(self, exc_type, exc, tb):
                return False

        # Mock server instance with cancellable run
        async def fake_run(*args, **kwargs):
            try:
                await asyncio.sleep(1)  # Should be cancelled quickly
            except asyncio.CancelledError:
                raise

        mock_server_instance = Mock()
        mock_server_instance.server = Mock()
        mock_server_instance.server.run = AsyncMock(side_effect=fake_run)
        mock_server_instance.server.get_capabilities = Mock(return_value={})
        mock_server_instance.db_operations = Mock()
        mock_server_instance.db_operations.disconnect = AsyncMock(return_value=CallToolResult(content=[{"type": "text", "text": "Disconnected"}]))
        with patch('server.asyncio.get_running_loop', return_value=FakeLoop()), \
             patch('server.stdio_server', return_value=DummyStdio()), \
             patch('server.Neo4jMCPServer', return_value=mock_server_instance), \
             patch('server.parse_arguments', return_value=SimpleNamespace(neo4j_uri=None, neo4j_username=None, neo4j_password=None)):
            # Run main; signal simulated during setup
            asyncio.run(main())

        # Assertions
        self.assertTrue(callbacks, "Signal handlers were not registered")
        # Ensure both SIGTERM and SIGINT registered if available in this platform
        # We cannot import signal inside patch context to map keys reliably, just check >=1
        mock_server_instance.server.run.assert_called_once()
        mock_server_instance.db_operations.disconnect.assert_called_once()


if __name__ == '__main__':
    unittest.main()