#!/usr/bin/env python3
"""
Unit tests for operations/observation_operations.py - Observation creation and deletion operations.
"""

import unittest
from unittest import IsolatedAsyncioTestCase  # Added
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from mcp.types import CallToolResult

# Import the observation operations module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j_mcp.operations.observation_operations import ObservationOperations


class TestObservationOperations(IsolatedAsyncioTestCase):  # Changed base class
    """Test cases for ObservationOperations class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_db.run_query = AsyncMock()
        # Add async connection check mock to prevent awaiting a plain Mock
        self.mock_db._check_connection = AsyncMock(return_value=None)
        self.obs_ops = ObservationOperations(self.mock_db)
    
    async def test_add_observations_success(self):
        """Test successful observation addition."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully added observation to entity 'John Doe': {'text': 'John is skilled', 'confidence': 0.9}"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe",
            "observation_text": "John is skilled",
            "confidence": 0.9,
            "tags": ["skill"]
        })
        
        self.assertFalse(result.isError)
        self.assertIn("John is skilled", result.content[0].text)
        self.assertIn("Successfully added observation", result.content[0].text)
    
    async def test_add_observations_with_timestamp(self):
        """Test observation addition with custom timestamp."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully added observation with timestamp: 2024-01-15T10:30:00"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe",
            "observation_text": "Test observation",
            "timestamp": "2024-01-15T10:30:00"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("2024-01-15T10:30:00", result.content[0].text)
    
    async def test_add_observations_with_source(self):
        """Test observation addition with source."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully added observation from source 'Lab Assistant'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe",
            "observation_text": "Test observation",
            "source": "Lab Assistant"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Lab Assistant", result.content[0].text)
    
    async def test_add_observations_missing_entity_id(self):
        """Test observation addition with missing entity_id."""
        result = await self.obs_ops.add_observations({
            "observation_text": "Test observation"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Entity ID is required", result.content[0].text)
    
    async def test_add_observations_missing_observation_text(self):
        """Test observation addition with missing observation_text."""
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Observation text is required", result.content[0].text)
    
    async def test_add_observations_error_handling(self):
        """Test observation addition error handling."""
        # Mock error response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Error adding observation: Database connection failed"}],
            isError=True
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe",
            "observation_text": "Test observation"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Error adding observation", result.content[0].text)
    
    async def test_delete_observations_by_id(self):
        """Test observation deletion by ID."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 1 observation(s) with ID 'obs123' from entity 'John Doe'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.delete_observations({
            "entity_id": "John Doe",
            "observation_id": "obs123"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)
        self.assertIn("obs123", result.content[0].text)
    
    async def test_delete_observations_by_text(self):
        """Test observation deletion by text."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 1 observation(s) with text 'Test observation' from entity 'John Doe'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.delete_observations({
            "entity_id": "John Doe",
            "observation_text": "Test observation"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)
        self.assertIn("Test observation", result.content[0].text)
    
    async def test_delete_observations_by_source(self):
        """Test observation deletion by source."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 2 observation(s) from source 'Lab Assistant' from entity 'John Doe'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.delete_observations({
            "entity_id": "John Doe",
            "source": "Lab Assistant"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)
        self.assertIn("Lab Assistant", result.content[0].text)
    
    async def test_delete_observations_by_tags(self):
        """Test observation deletion by tags."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 1 observation(s) with tags ['research'] from entity 'John Doe'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.delete_observations({
            "entity_id": "John Doe",
            "tags": ["research"]
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)
        self.assertIn("research", result.content[0].text)
    
    async def test_delete_all_observations(self):
        """Test deletion of all observations for an entity."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted 3 observation(s) from entity 'John Doe'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.delete_observations({
            "entity_id": "John Doe"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)
        self.assertIn("3 observation(s)", result.content[0].text)
    
    async def test_delete_observations_missing_entity_id(self):
        """Test observation deletion with missing entity_id."""
        result = await self.obs_ops.delete_observations({
            "observation_id": "obs123"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Entity ID is required", result.content[0].text)
    
    async def test_delete_observations_error_handling(self):
        """Test observation deletion error handling."""
        # Mock error response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Error deleting observations: Database connection failed"}],
            isError=True
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.delete_observations({
            "entity_id": "John Doe",
            "observation_id": "obs123"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Error deleting observations", result.content[0].text)


class TestObservationOperationsIntegration(unittest.TestCase):
    """Integration tests for observation operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.obs_ops = ObservationOperations(self.mock_db)
    
    def test_class_has_required_methods(self):
        """Test that ObservationOperations has all required methods."""
        required_methods = ['add_observations', 'delete_observations']
        
        for method in required_methods:
            self.assertTrue(hasattr(self.obs_ops, method), f"Missing method: {method}")
    
    def test_class_has_required_attributes(self):
        """Test that ObservationOperations has all required attributes."""
        self.assertTrue(hasattr(self.obs_ops, 'db_operations'))
        self.assertEqual(self.obs_ops.db_operations, self.mock_db)


class TestObservationOperationsEdgeCases(IsolatedAsyncioTestCase):  # Changed base class
    """Edge case tests for observation operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_db.run_query = AsyncMock()
        # Add async connection check mock
        self.mock_db._check_connection = AsyncMock(return_value=None)
        self.obs_ops = ObservationOperations(self.mock_db)
    
    async def test_add_observations_with_complex_metadata(self):
        """Test observation addition with complex metadata."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully added observation with complex metadata"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe",
            "observation_text": "Complex observation with metadata",
            "confidence": 0.95,
            "source": "AI System",
            "tags": ["research", "neural-networks", "ongoing"],
            "timestamp": "2024-01-15T10:30:00Z"
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Successfully added observation", result.content[0].text)
    
    async def test_add_observations_with_empty_text(self):
        """Test observation addition with empty text."""
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe",
            "observation_text": ""
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Observation text cannot be empty", result.content[0].text)
    
    async def test_add_observations_with_empty_entity_id(self):
        """Test observation addition with empty entity ID."""
        result = await self.obs_ops.add_observations({
            "entity_id": "",
            "observation_text": "Test observation"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Entity ID cannot be empty", result.content[0].text)
    
    async def test_add_observations_with_very_long_text(self):
        """Test observation addition with very long text."""
        long_text = "A" * 10000
        mock_result = CallToolResult(
            content=[{"type": "text", "text": f"Successfully added observation with long text: {long_text[:100]}..."}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe",
            "observation_text": long_text
        })
        
        self.assertFalse(result.isError)
        self.assertIn("Successfully added observation", result.content[0].text)
    
    async def test_add_observations_with_invalid_confidence(self):
        """Test observation addition with invalid confidence."""
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe",
            "observation_text": "Test observation",
            "confidence": 1.5  # Invalid confidence > 1.0
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Confidence must be between 0.0 and 1.0", result.content[0].text)
    
    async def test_add_observations_with_negative_confidence(self):
        """Test observation addition with negative confidence."""
        result = await self.obs_ops.add_observations({
            "entity_id": "John Doe",
            "observation_text": "Test observation",
            "confidence": -0.1  # Invalid negative confidence
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Confidence must be between 0.0 and 1.0", result.content[0].text)
    
    async def test_delete_observations_with_empty_entity_id(self):
        """Test observation deletion with empty entity ID."""
        result = await self.obs_ops.delete_observations({
            "entity_id": "",
            "observation_id": "obs123"
        })
        
        self.assertTrue(result.isError)
        self.assertIn("Entity ID cannot be empty", result.content[0].text)
    
    async def test_delete_observations_with_empty_observation_id(self):
        """Test observation deletion with empty observation ID."""
        # Mock successful response
        mock_result = CallToolResult(
            content=[{"type": "text", "text": "Successfully deleted all observations from entity 'John Doe'"}],
            isError=False
        )
        self.mock_db.run_query.return_value = mock_result
        
        result = await self.obs_ops.delete_observations({
            "entity_id": "John Doe",
            "observation_id": ""
        })
        
        self.assertFalse(result.isError)
        self.assertIn("deleted", result.content[0].text)


if __name__ == '__main__':
    unittest.main()