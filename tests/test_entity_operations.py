#!/usr/bin/env python3
"""
Unit tests for operations/entity_operations.py - Entity creation and deletion operations.
"""

import unittest
from unittest import IsolatedAsyncioTestCase  # Added
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from mcp.types import CallToolResult

# Import the entity operations module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from operations.entity_operations import EntityOperations


class TestEntityOperations(IsolatedAsyncioTestCase):  # Changed base class
    """Test cases for EntityOperations class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_db.run_query = AsyncMock()
        # Add async connection check mock to prevent TypeError from awaiting a plain Mock
        self.mock_db._check_connection = AsyncMock(return_value=None)
        self.entity_ops = EntityOperations(self.mock_db)
    
    async def test_create_entities_success(self):
        """Test successful entity creation."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully created Person entity: {'name': 'John Doe', 'age': 30}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.entity_ops.create_entities({
            "entity_type": "Person",
            "properties": {"name": "John Doe", "age": 30}
        })
        
        self.assertFalse(result.isError)
        self.assertIn("John Doe", result.content[0].text)
        self.assertIn("Successfully created", result.content[0].text)
    
    async def test_create_entities_with_labels(self):
        """Test entity creation with additional labels."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully created Person entity with labels: ['Person', 'Employee']"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.entity_ops.create_entities({
            "entity_type": "Person",
            "properties": {"name": "John Doe"},
            "labels": ["Employee"]
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Employee", result.content[0].text)
        self.assertIn("Successfully created", result.content[0].text)
    
    async def test_create_entities_missing_entity_type(self):
        """Test entity creation with missing entity_type."""
        result = await self.entity_ops.create_entities({
            "properties": {"name": "John Doe"}
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Entity type is required", result.content[0].text)
    
    async def test_create_entities_missing_properties(self):
        """Test entity creation with missing properties."""
        result = await self.entity_ops.create_entities({
            "entity_type": "Person"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Properties are required", result.content[0].text)
    
    async def test_create_entities_missing_name(self):
        """Test entity creation with missing name property."""
        result = await self.entity_ops.create_entities({
            "entity_type": "Person",
            "properties": {"age": 30}
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Name or id property is required", result.content[0].text)
    
    async def test_create_entities_error_handling(self):
        """Test entity creation error handling."""
        # Mock error response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Error creating entity: Database connection failed"}],
            isError=True
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.entity_ops.create_entities({
            "entity_type": "Person",
            "properties": {"name": "John Doe", "age": 30}
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Error creating entity", result.content[0].text)
    
    async def test_delete_entities_success(self):
        """Test successful entity deletion."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 1 entity(ies) and their relationships"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.entity_ops.delete_entities({
            "entity_id": "John Doe",
            "delete_relationships": True
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)
        self.assertIn("1 entity(ies)", result.content[0].text)
    
    async def test_delete_entities_without_relationships(self):
        """Test entity deletion without deleting relationships."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 1 entity(ies)"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.entity_ops.delete_entities({
            "entity_id": "John Doe",
            "delete_relationships": False
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)
        self.assertIn("1 entity(ies)", result.content[0].text)
    
    async def test_delete_entities_missing_entity_id(self):
        """Test entity deletion with missing entity_id."""
        result = await self.entity_ops.delete_entities({})
        
        self.assertTrue(result.isError)
        self.assertIn("Entity ID is required", result.content[0].text)
    
    async def test_delete_entities_error_handling(self):
        """Test entity deletion error handling."""
        # Mock error response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Error deleting entity: Database connection failed"}],
            isError=True
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.entity_ops.delete_entities({
            "entity_id": "John Doe"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Error deleting entity", result.content[0].text)
    
    async def test_delete_entities_with_entity_type_filter(self):
        """Test entity deletion with entity type filter."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 1 Person entity(ies) and their relationships"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.entity_ops.delete_entities({
            "entity_id": "John Doe",
            "entity_type": "Person",
            "delete_relationships": True
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Person entity(ies)", result.content[0].text)
        self.assertIn("deleted", result.content[0].text)


class TestEntityOperationsIntegration(unittest.TestCase):
    """Integration tests for entity operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.entity_ops = EntityOperations(self.mock_db)
    
    def test_class_has_required_methods(self):
        """Test that EntityOperations has all required methods."""
        required_methods = ['create_entities', 'delete_entities']
        
        for method in required_methods:
            self.assertTrue(hasattr(self.entity_ops, method), f"Missing method: {method}")
    
    def test_class_has_required_attributes(self):
        """Test that EntityOperations has all required attributes."""
        self.assertTrue(hasattr(self.entity_ops, 'db_operations'))
        self.assertEqual(self.entity_ops.db_operations, self.mock_db)


class TestEntityOperationsEdgeCases(IsolatedAsyncioTestCase):  # Changed base class
    """Edge case tests for entity operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_db.run_query = AsyncMock()
        # Add async connection check mock
        self.mock_db._check_connection = AsyncMock(return_value=None)
        self.entity_ops = EntityOperations(self.mock_db)
    
    async def test_create_entities_with_id_property(self):
        """Test entity creation with id property instead of name."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully created Person entity: {'id': '12345', 'age': 30}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.entity_ops.create_entities({
            "entity_type": "Person",
            "properties": {"id": "12345", "age": 30}
        })
        
        self.assertFalse(result.isError)
        self.assertIn("12345", result.content[0].text)
        self.assertIn("Successfully created", result.content[0].text)
    
    async def test_create_entities_with_complex_properties(self):
        """Test entity creation with complex properties."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully created Person entity with complex properties"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        complex_properties = {
            "name": "John Doe",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zip": "10001"
            },
            "skills": ["Python", "Neo4j", "GraphQL"],
            "metadata": {
                "created_at": "2024-01-01",
                "version": 1.0
            }
        }
        
        result = await self.entity_ops.create_entities({
            "entity_type": "Person",
            "properties": complex_properties
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Successfully created", result.content[0].text)
    
    async def test_create_entities_with_empty_properties(self):
        """Test entity creation with empty properties."""
        result = await self.entity_ops.create_entities({
            "entity_type": "Person",
            "properties": {}
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Name or id property is required", result.content[0].text)
    
    async def test_create_entities_with_empty_entity_type(self):
        """Test entity creation with empty entity type."""
        result = await self.entity_ops.create_entities({
            "entity_type": "",
            "properties": {"name": "John Doe"}
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Entity type cannot be empty", result.content[0].text)
    
    async def test_delete_entities_with_empty_entity_id(self):
        """Test entity deletion with empty entity ID."""
        result = await self.entity_ops.delete_entities({
            "entity_id": ""
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Entity ID cannot be empty", result.content[0].text)
    
    async def test_delete_entities_with_very_long_entity_id(self):
        """Test entity deletion with very long entity ID."""
        long_id = "A" * 1000
        mock_result = CallToolResult(
            content=[{"type": "text", "text": f"Successfully deleted 1 entity(ies) with ID '{long_id}'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.entity_ops.delete_entities({
            "entity_id": long_id
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)


if __name__ == '__main__':
    unittest.main()