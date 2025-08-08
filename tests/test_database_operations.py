#!/usr/bin/env python3
"""
Unit tests for database/operations.py - Database connection and query operations.
"""

import unittest
from unittest import IsolatedAsyncioTestCase  # Added for async test support
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from mcp.types import CallToolResult

# Import the database operations module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j_mcp.database.operations import Neo4jOperations


class TestNeo4jOperations(IsolatedAsyncioTestCase):  # Changed base class for async tests
    """Test cases for Neo4jOperations class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db_ops = Neo4jOperations()
    
    def test_initialization(self):
        """Test Neo4jOperations initialization."""
        self.assertIsNotNone(self.db_ops)
        self.assertIsNone(self.db_ops.driver)
    
    @patch('database.operations.AsyncGraphDatabase')
    async def test_connect_success(self, mock_graph_db):
        """Test successful database connection."""
        # Mock the driver
        mock_driver = Mock()
        mock_driver.verify_connectivity = AsyncMock()
        mock_graph_db.driver.return_value = mock_driver
        
        result = await self.db_ops.connect(
            "neo4j://localhost:7687",
            "neo4j",
            "password"
        )
        
        self.assertFalse(result.isError)
        self.assertIn("Successfully connected", result.content[0].text)
        self.assertEqual(self.db_ops.driver, mock_driver)
        mock_graph_db.driver.assert_called_once_with(
            "neo4j://localhost:7687", auth=("neo4j", "password")
        )
    
    @patch('database.operations.AsyncGraphDatabase')
    async def test_connect_failure(self, mock_graph_db):
        """Test failed database connection."""
        # Mock connection failure
        mock_graph_db.driver.side_effect = Exception("Connection failed")
        
        result = await self.db_ops.connect(
            "neo4j://localhost:7687",
            "neo4j",
            "wrong_password"
        )
        
        self.assertTrue(result.isError)
        self.assertIn("Failed to connect", result.content[0].text)
        self.assertIsNone(self.db_ops.driver)
    
    async def test_run_query_success(self):
        """Test successful query execution."""
        # Mock the driver and session
        mock_session = Mock()
        mock_result = Mock()
        mock_result.data = AsyncMock(return_value=[{"name": "Test", "value": 42}])
        
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        self.db_ops.driver = Mock()
        self.db_ops.driver.session = Mock(return_value=mock_session)
        
        result = await self.db_ops.run_query(
            "MATCH (n) RETURN n LIMIT 5",
            {"limit": 5}
        )
        
        self.assertFalse(result.isError)
        self.assertIn("Query Results", result.content[0].text)
        mock_session.run.assert_called_once_with(
            "MATCH (n) RETURN n LIMIT 5", {"limit": 5}
        )
    
    async def test_run_query_failure(self):
        """Test failed query execution."""
        # Mock the driver and session with error
        mock_session = Mock()
        mock_session.run = AsyncMock(side_effect=Exception("Query failed"))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        self.db_ops.driver = Mock()
        self.db_ops.driver.session = Mock(return_value=mock_session)
        
        result = await self.db_ops.run_query(
            "INVALID CYPHER QUERY",
            {}
        )
        
        self.assertTrue(result.isError)
        self.assertIn("Query execution failed", result.content[0].text)
    
    async def test_run_query_no_driver(self):
        """Test query execution without driver."""
        result = await self.db_ops.run_query("MATCH (n) RETURN n", {})
        
        self.assertTrue(result.isError)
        self.assertIn("Not connected to Neo4j", result.content[0].text)
    
    async def test_disconnect_success(self):
        """Test successful database disconnection."""
        mock_driver = Mock()
        mock_driver.close = AsyncMock()
        self.db_ops.driver = mock_driver
        
        result = await self.db_ops.disconnect()
        
        self.assertFalse(result.isError)
        self.assertIn("Successfully disconnected", result.content[0].text)
        mock_driver.close.assert_called_once()
        self.assertIsNone(self.db_ops.driver)
    
    async def test_disconnect_no_driver(self):
        """Test disconnection without driver."""
        result = await self.db_ops.disconnect()
        
        self.assertFalse(result.isError)
        self.assertIn("Not connected to Neo4j", result.content[0].text)


class TestNeo4jOperationsIntegration(unittest.TestCase):
    """Integration tests for database operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db_ops = Neo4jOperations()
    
    def test_class_has_required_methods(self):
        """Test that Neo4jOperations has all required methods."""
        required_methods = [
            'connect', 'disconnect', 'run_query'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(self.db_ops, method), f"Missing method: {method}")
    
    def test_class_has_required_attributes(self):
        """Test that Neo4jOperations has all required attributes."""
        self.assertTrue(hasattr(self.db_ops, 'driver'))
        self.assertIsNone(self.db_ops.driver)  # Should be None initially


if __name__ == '__main__':
    unittest.main()