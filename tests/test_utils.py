#!/usr/bin/env python3
"""
Unit tests for utils/validators.py - Validation utilities.
"""

import unittest
from unittest.mock import Mock, patch

# Import the utils module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j_mcp.utils.validators import (
    validate_confidence,
    validate_entity_properties
)


class TestValidators(unittest.TestCase):
    """Test cases for validation utilities."""
    
    def test_validate_confidence_valid(self):
        """Test validation of valid confidence values."""
        valid_confidences = [None, 0.0, 0.5, 1.0, 0.999]
        
        for confidence in valid_confidences:
            is_valid, error = validate_confidence(confidence)
            self.assertTrue(is_valid, f"Confidence should be valid: {confidence}")
            self.assertEqual(error, "")
    
    def test_validate_confidence_invalid(self):
        """Test validation of invalid confidence values."""
        invalid_confidences = [
            (-0.1, "Confidence must be between 0.0 and 1.0"),
            (1.1, "Confidence must be between 0.0 and 1.0"),
            ("0.5", "Confidence must be a number"),
            ([0.5], "Confidence must be a number")
        ]
        
        for confidence, expected_error in invalid_confidences:
            is_valid, error = validate_confidence(confidence)
            self.assertFalse(is_valid, f"Confidence should be invalid: {confidence}")
            self.assertIn(expected_error, error)
    
    def test_validate_entity_properties_valid(self):
        """Test validation of valid entity properties."""
        valid_properties = [
            {"name": "John Doe"},
            {"id": "12345"},
            {"name": "John Doe", "age": 30},
            {"id": "12345", "type": "Person"}
        ]
        
        for props in valid_properties:
            is_valid, error = validate_entity_properties(props)
            self.assertTrue(is_valid, f"Properties should be valid: {props}")
            self.assertEqual(error, "")
    
    def test_validate_entity_properties_invalid(self):
        """Test validation of invalid entity properties."""
        invalid_properties = [
            ({}, "Entity properties must include 'name' or 'id'"),
            ({"age": 30}, "Entity properties must include 'name' or 'id'"),
            (None, "Properties must be a dictionary"),
            ("not a dict", "Properties must be a dictionary"),
            ([], "Properties must be a dictionary")
        ]
        
        for props, expected_error in invalid_properties:
            is_valid, error = validate_entity_properties(props)
            self.assertFalse(is_valid, f"Properties should be invalid: {props}")
            self.assertIn(expected_error, error)


class TestValidatorsEdgeCases(unittest.TestCase):
    """Edge case tests for validation utilities."""
    
    def test_validate_confidence_edge_cases(self):
        """Test validation of edge case confidence values."""
        edge_cases = [
            (0.0, True),      # Minimum valid
            (1.0, True),      # Maximum valid
            (0.999999, True), # Very close to 1.0
            (0.000001, True), # Very close to 0.0
            (-0.000001, False), # Just below 0.0
            (1.000001, False),  # Just above 1.0
        ]
        
        for confidence, expected_valid in edge_cases:
            is_valid, error = validate_confidence(confidence)
            self.assertEqual(is_valid, expected_valid, f"Confidence: {confidence}")
    
    def test_validate_entity_properties_edge_cases(self):
        """Test validation of edge case entity properties."""
        edge_cases = [
            ({"name": "A" * 1000}, True),  # Very long name
            ({"id": "12345" * 100}, True),  # Very long id
            ({"name": "", "id": "123"}, True),  # Empty name but has id
            ({"name": "John", "id": ""}, True),  # Empty id but has name
            ({"name": "", "id": ""}, True),  # Both empty but present
        ]
        
        for props, expected_valid in edge_cases:
            is_valid, error = validate_entity_properties(props)
            self.assertEqual(is_valid, expected_valid, f"Properties: {props}")


class TestValidatorsIntegration(unittest.TestCase):
    """Integration tests for validation utilities."""
    
    def test_all_validator_functions_exist(self):
        """Test that all expected validator functions exist."""
        expected_functions = [
            'validate_confidence',
            'validate_entity_properties'
        ]
        
        for func_name in expected_functions:
            self.assertTrue(hasattr(sys.modules['utils.validators'], func_name),
                          f"Missing validator function: {func_name}")
    
    def test_validator_return_format(self):
        """Test that all validators return the expected format."""
        validators = [
            validate_confidence,
            validate_entity_properties
        ]
        
        for validator in validators:
            # Test with a valid input
            if validator == validate_confidence:
                result = validator(0.5)
            elif validator == validate_entity_properties:
                result = validator({"name": "Test"})
            
            # Check return format
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], bool)
            self.assertIsInstance(result[1], str)
    
    def test_validator_error_messages(self):
        """Test that validators provide meaningful error messages."""
        # Test invalid confidence
        is_valid, error = validate_confidence(1.5)
        self.assertFalse(is_valid)
        self.assertIsInstance(error, str)
        self.assertGreater(len(error), 0)
        
        # Test invalid entity properties
        is_valid, error = validate_entity_properties({})
        self.assertFalse(is_valid)
        self.assertIsInstance(error, str)
        self.assertGreater(len(error), 0)


if __name__ == '__main__':
    unittest.main() 