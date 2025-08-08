#!/usr/bin/env python3
"""
Unit tests for operations/search_operations.py - Search and find operations.
"""

import unittest
from unittest import IsolatedAsyncioTestCase  # Added
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from mcp.types import CallToolResult

# Import the search operations module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from operations.search_operations import SearchOperations


class TestSearchOperations(IsolatedAsyncioTestCase):  # Changed base class
    """Test cases for SearchOperations class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_db.run_query = AsyncMock()
        # Async connection check mock
        self.mock_db._check_connection = AsyncMock(return_value=None)
        self.search_ops = SearchOperations(self.mock_db)
    
    async def test_find_nodes_exact_match_success(self):
        """Test find_nodes with exact match success."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Found 1 node(s) matching 'Test':\nNode 1: {'name': 'Test', 'age': 30}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.find_nodes({
            "name": "Test",
            "exact_match": True,
            "case_sensitive": True
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Test", result.content[0].text)
        self.assertIn("Found 1 node(s)", result.content[0].text)
    
    async def test_find_nodes_partial_match_success(self):
        """Test find_nodes with partial match success."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Found 2 node(s) matching 'Test':\nNode 1: {'name': 'Test1'}\nNode 2: {'name': 'Test2'}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.find_nodes({
            "name": "Test",
            "exact_match": False,
            "case_sensitive": False
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Test1", result.content[0].text)
        self.assertIn("Test2", result.content[0].text)
        self.assertIn("Found 2 node(s)", result.content[0].text)
    
    async def test_find_nodes_case_insensitive(self):
        """Test find_nodes with case insensitive search."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Found 1 node(s) matching 'test':\nNode 1: {'name': 'Test', 'age': 30}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.find_nodes({
            "name": "test",
            "exact_match": True,
            "case_sensitive": False
        })
        
        self.assertFalse(result.isError)
        self.assertIn("test", result.content[0].text)
    
    async def test_find_nodes_error_handling(self):
        """Test find_nodes error handling."""
        # Mock error response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Error finding nodes: Database connection failed"}],
            isError=True
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.find_nodes({
            "name": "Test"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Error finding nodes", result.content[0].text)
    
    async def test_find_nodes_missing_name(self):
        """Test find_nodes with missing name parameter."""
        result = await self.search_ops.find_nodes({})
        
        self.assertTrue(result.isError)
        self.assertIn("Name parameter is required", result.content[0].text)
    
    async def test_search_nodes_success(self):
        """Test search_nodes success."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Found 1 node(s) containing 'Test' in any property:\nNode 1: {'name': 'Test', 'city': 'TestCity'}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.search_nodes({
            "search_string": "Test",
            "case_sensitive": True
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Test", result.content[0].text)
        self.assertIn("Found 1 node(s)", result.content[0].text)
    
    async def test_search_nodes_case_insensitive(self):
        """Test search_nodes with case insensitive search."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Found 1 node(s) containing 'test' in any property:\nNode 1: {'name': 'Test', 'city': 'TestCity'}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.search_nodes({
            "search_string": "test",
            "case_sensitive": False
        })
        
        self.assertFalse(result.isError)
        self.assertIn("test", result.content[0].text)
    
    async def test_search_nodes_with_property_name(self):
        """Test search_nodes with specific property name."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Found 1 node(s) containing 'Test' in property 'name':\nNode 1: {'name': 'Test'}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.search_nodes({
            "search_string": "Test",
            "property_name": "name",
            "case_sensitive": True
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Test", result.content[0].text)
        self.assertIn("property 'name'", result.content[0].text)
    
    async def test_search_nodes_error_handling(self):
        """Test search_nodes error handling."""
        # Mock error response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Error searching nodes: Database connection failed"}],
            isError=True
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.search_nodes({
            "search_string": "test"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Error searching nodes", result.content[0].text)
    
    async def test_search_nodes_missing_search_string(self):
        """Test search_nodes with missing search_string parameter."""
        result = await self.search_ops.search_nodes({})
        
        self.assertTrue(result.isError)
        self.assertIn("Search string parameter is required", result.content[0].text)
    
    async def test_search_nodes_empty_search_string(self):
        """Test search_nodes with empty search string."""
        result = await self.search_ops.search_nodes({
            "search_string": ""
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Search string cannot be empty", result.content[0].text)
    
    async def test_find_nodes_empty_name(self):
        """Test find_nodes with empty name."""
        result = await self.search_ops.find_nodes({
            "name": ""
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Name cannot be empty", result.content[0].text)


class TestSearchOperationsIntegration(unittest.TestCase):
    """Integration tests for search operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.search_ops = SearchOperations(self.mock_db)
    
    def test_class_has_required_methods(self):
        """Test that SearchOperations has all required methods."""
        required_methods = ['find_nodes', 'search_nodes']
        
        for method in required_methods:
            self.assertTrue(hasattr(self.search_ops, method), f"Missing method: {method}")
    
    def test_class_has_required_attributes(self):
        """Test that SearchOperations has all required attributes."""
        self.assertTrue(hasattr(self.search_ops, 'db_operations'))
        self.assertEqual(self.search_ops.db_operations, self.mock_db)


class TestSearchOperationsEdgeCases(IsolatedAsyncioTestCase):  # Changed base class
    """Edge case tests for search operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_db.run_query = AsyncMock()
        self.mock_db._check_connection = AsyncMock(return_value=None)
        self.search_ops = SearchOperations(self.mock_db)
    
    async def test_find_nodes_very_long_name(self):
        """Test find_nodes with very long name."""
        long_name = "A" * 1000
        mock_result = CallToolResult(
            content=[{"type": "text", "text": f"Found 0 node(s) matching '{long_name}':"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.find_nodes({
            "name": long_name,
            "exact_match": True
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Found 0 node(s)", result.content[0].text)
    
    async def test_search_nodes_special_characters(self):
        """Test search_nodes with special characters."""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        mock_result = CallToolResult(
            content=[{"type": "text", "text": f"Found 0 node(s) containing '{special_chars}' in any property:"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.search_nodes({
            "search_string": special_chars
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Found 0 node(s)", result.content[0].text)
    
    async def test_search_nodes_unicode_characters(self):
        """Test search_nodes with unicode characters."""
        unicode_chars = "测试中文 🚀 émojis"
        mock_result = CallToolResult(
            content=[{"type": "text", "text": f"Found 0 node(s) containing '{unicode_chars}' in any property:"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.search_ops.search_nodes({
            "search_string": unicode_chars
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Found 0 node(s)", result.content[0].text)


if __name__ == '__main__':
    unittest.main()