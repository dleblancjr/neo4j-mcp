"""
Validation utilities for the Neo4j MCP server.
Contains shared validation functions.
"""

from typing import Dict, Any, Optional, Tuple


def validate_confidence(confidence: Optional[float]) -> Tuple[bool, str]:
    """
    Validate confidence value.
    
    Args:
        confidence: Confidence value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if confidence is None:
        return True, ""
    
    if not isinstance(confidence, (int, float)):
        return False, "Confidence must be a number"
    
    if not (0.0 <= confidence <= 1.0):
        return False, "Confidence must be between 0.0 and 1.0"
    
    return True, ""


def validate_entity_properties(properties: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate entity properties.
    
    Args:
        properties: Properties dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(properties, dict):
        return False, "Properties must be a dictionary"
    
    if "name" not in properties and "id" not in properties:
        # Updated to match test expectation
        return False, "Entity properties must include 'name' or 'id'"
    
    return True, ""


