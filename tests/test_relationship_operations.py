#!/usr/bin/env python3
"""
Unit tests for operations/relationship_operations.py - Relationship creation and deletion operations.
"""

import unittest
from unittest import IsolatedAsyncioTestCase  # Added
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from mcp.types import CallToolResult

# Import the relationship operations module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from operations.relationship_operations import RelationshipOperations


class TestRelationshipOperations(IsolatedAsyncioTestCase):  # Changed base class
    """Test cases for RelationshipOperations class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_db.run_query = AsyncMock()
        # Add async connection check mock
        self.mock_db._check_connection = AsyncMock(return_value=None)
        self.rel_ops = RelationshipOperations(self.mock_db)
    
    async def test_create_relations_success(self):
        """Test successful relationship creation."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully created KNOWS relationship: {'since': 2020}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.rel_ops.create_relations({
            "source_id": "Alice",
            "target_id": "Bob",
            "relationship_type": "KNOWS",
            "properties": {"since": 2020}
        })
        
        self.assertFalse(result.isError)
        self.assertIn("KNOWS", result.content[0].text)
        self.assertIn("Successfully created", result.content[0].text)
    
    async def test_create_relations_without_properties(self):
        """Test relationship creation without properties."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully created KNOWS relationship"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.rel_ops.create_relations({
            "source_id": "Alice",
            "target_id": "Bob",
            "relationship_type": "KNOWS"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("KNOWS", result.content[0].text)
        self.assertIn("Successfully created", result.content[0].text)
    
    async def test_create_relations_missing_source_id(self):
        """Test relationship creation with missing source_id."""
        result = await self.rel_ops.create_relations({
            "target_id": "Bob",
            "relationship_type": "KNOWS"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Source ID is required", result.content[0].text)
    
    async def test_create_relations_missing_target_id(self):
        """Test relationship creation with missing target_id."""
        result = await self.rel_ops.create_relations({
            "source_id": "Alice",
            "relationship_type": "KNOWS"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Target ID is required", result.content[0].text)
    
    async def test_create_relations_missing_relationship_type(self):
        """Test relationship creation with missing relationship_type."""
        result = await self.rel_ops.create_relations({
            "source_id": "Alice",
            "target_id": "Bob"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Relationship type is required", result.content[0].text)
    
    async def test_create_relations_error_handling(self):
        """Test relationship creation error handling."""
        # Mock error response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Error creating relationship: Database connection failed"}],
            isError=True
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.rel_ops.create_relations({
            "source_id": "Alice",
            "target_id": "Bob",
            "relationship_type": "KNOWS"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Error creating relationship", result.content[0].text)
    
    async def test_delete_relations_success(self):
        """Test successful relationship deletion."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 1 relationship(s) of type 'KNOWS' between 'Alice' and 'Bob'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.rel_ops.delete_relations({
            "source_id": "Alice",
            "target_id": "Bob",
            "relationship_type": "KNOWS"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)
        self.assertIn("KNOWS", result.content[0].text)
    
    async def test_delete_all_relations(self):
        """Test deletion of all relationships between entities."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 2 relationship(s) between 'Alice' and 'Bob'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.rel_ops.delete_relations({
            "source_id": "Alice",
            "target_id": "Bob"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)
        self.assertIn("2 relationship(s)", result.content[0].text)
    
    async def test_delete_relations_missing_source_id(self):
        """Test relationship deletion with missing source_id."""
        result = await self.rel_ops.delete_relations({
            "target_id": "Bob",
            "relationship_type": "KNOWS"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Source ID is required", result.content[0].text)
    
    async def test_delete_relations_missing_target_id(self):
        """Test relationship deletion with missing target_id."""
        result = await self.rel_ops.delete_relations({
            "source_id": "Alice",
            "relationship_type": "KNOWS"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Target ID is required", result.content[0].text)
    
    async def test_delete_relations_error_handling(self):
        """Test relationship deletion error handling."""
        # Mock error response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Error deleting relationship: Database connection failed"}],
            isError=True
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.rel_ops.delete_relations({
            "source_id": "Alice",
            "target_id": "Bob",
            "relationship_type": "KNOWS"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Error deleting relationship", result.content[0].text)


class TestRelationshipOperationsIntegration(unittest.TestCase):
    """Integration tests for relationship operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.rel_ops = RelationshipOperations(self.mock_db)
    
    def test_class_has_required_methods(self):
        """Test that RelationshipOperations has all required methods."""
        required_methods = ['create_relations', 'delete_relations']
        
        for method in required_methods:
            self.assertTrue(hasattr(self.rel_ops, method), f"Missing method: {method}")
    
    def test_class_has_required_attributes(self):
        """Test that RelationshipOperations has all required attributes."""
        self.assertTrue(hasattr(self.rel_ops, 'db_operations'))
        self.assertEqual(self.rel_ops.db_operations, self.mock_db)


if __name__ == '__main__':
    unittest.main()