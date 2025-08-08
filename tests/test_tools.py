#!/usr/bin/env python3
"""
Unit tests for tools/tool_definitions.py - Tool definitions and schemas.
"""

import unittest
from unittest.mock import Mock, patch

# Import the tools module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.tool_definitions import get_all_tools
from mcp.types import Tool


class TestToolDefinitions(unittest.TestCase):
    """Test cases for tool definitions."""
    
    def test_get_all_tools_returns_list(self):
        """Test that get_all_tools returns a list."""
        tools = get_all_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
    
    def test_all_tools_are_tool_objects(self):
        """Test that all returned items are Tool objects."""
        tools = get_all_tools()
        for tool in tools:
            self.assertIsInstance(tool, Tool)
    
    def test_tools_have_required_attributes(self):
        """Test that all tools have required attributes."""
        tools = get_all_tools()
        for tool in tools:
            self.assertTrue(hasattr(tool, 'name'))
            self.assertTrue(hasattr(tool, 'description'))
            self.assertTrue(hasattr(tool, 'inputSchema'))
            self.assertIsInstance(tool.name, str)
            self.assertIsInstance(tool.description, str)
            self.assertIsInstance(tool.inputSchema, dict)
    
    def test_connect_neo4j_tool_exists(self):
        """Test that connect_neo4j tool exists and has correct schema."""
        tools = get_all_tools()
        connect_tool = next((t for t in tools if t.name == "connect_neo4j"), None)
        
        self.assertIsNotNone(connect_tool)
        self.assertEqual(connect_tool.name, "connect_neo4j")
        self.assertIn("Connect to a Neo4j database", connect_tool.description)
        
        # Check schema
        schema = connect_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("uri", properties)
        self.assertIn("username", properties)
        self.assertIn("password", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("uri", required)
        self.assertIn("username", required)
        self.assertIn("password", required)
    
    def test_run_cypher_query_tool_exists(self):
        """Test that run_cypher_query tool exists and has correct schema."""
        tools = get_all_tools()
        query_tool = next((t for t in tools if t.name == "run_cypher_query"), None)
        
        self.assertIsNotNone(query_tool)
        self.assertEqual(query_tool.name, "run_cypher_query")
        self.assertIn("Run a Cypher query", query_tool.description)
        
        # Check schema
        schema = query_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("query", properties)
        self.assertIn("parameters", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("query", required)
    
    def test_find_nodes_tool_exists(self):
        """Test that find_nodes tool exists and has correct schema."""
        tools = get_all_tools()
        find_tool = next((t for t in tools if t.name == "find_nodes"), None)
        
        self.assertIsNotNone(find_tool)
        self.assertEqual(find_tool.name, "find_nodes")
        self.assertIn("Find nodes by name", find_tool.description)
        
        # Check schema
        schema = find_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("name", properties)
        self.assertIn("exact_match", properties)
        self.assertIn("case_sensitive", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("name", required)
    
    def test_search_nodes_tool_exists(self):
        """Test that search_nodes tool exists and has correct schema."""
        tools = get_all_tools()
        search_tool = next((t for t in tools if t.name == "search_nodes"), None)
        
        self.assertIsNotNone(search_tool)
        self.assertEqual(search_tool.name, "search_nodes")
        self.assertIn("Search nodes by string", search_tool.description)
        
        # Check schema
        schema = search_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("search_string", properties)
        self.assertIn("property_name", properties)
        self.assertIn("case_sensitive", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("search_string", required)
    
    def test_create_entities_tool_exists(self):
        """Test that create_entities tool exists and has correct schema."""
        tools = get_all_tools()
        create_tool = next((t for t in tools if t.name == "create_entities"), None)
        
        self.assertIsNotNone(create_tool)
        self.assertEqual(create_tool.name, "create_entities")
        self.assertIn("Create memory entities", create_tool.description)
        
        # Check schema
        schema = create_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("entity_type", properties)
        self.assertIn("properties", properties)
        self.assertIn("labels", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("entity_type", required)
        self.assertIn("properties", required)
    
    def test_delete_entities_tool_exists(self):
        """Test that delete_entities tool exists and has correct schema."""
        tools = get_all_tools()
        delete_tool = next((t for t in tools if t.name == "delete_entities"), None)
        
        self.assertIsNotNone(delete_tool)
        self.assertEqual(delete_tool.name, "delete_entities")
        self.assertIn("Delete memory entities", delete_tool.description)
        
        # Check schema
        schema = delete_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("entity_id", properties)
        self.assertIn("entity_type", properties)
        self.assertIn("delete_relationships", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("entity_id", required)
    
    def test_create_relations_tool_exists(self):
        """Test that create_relations tool exists and has correct schema."""
        tools = get_all_tools()
        create_rel_tool = next((t for t in tools if t.name == "create_relations"), None)
        
        self.assertIsNotNone(create_rel_tool)
        self.assertEqual(create_rel_tool.name, "create_relations")
        self.assertIn("Create relationships", create_rel_tool.description)
        
        # Check schema
        schema = create_rel_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("source_id", properties)
        self.assertIn("target_id", properties)
        self.assertIn("relationship_type", properties)
        self.assertIn("properties", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("source_id", required)
        self.assertIn("target_id", required)
        self.assertIn("relationship_type", required)
    
    def test_delete_relations_tool_exists(self):
        """Test that delete_relations tool exists and has correct schema."""
        tools = get_all_tools()
        delete_rel_tool = next((t for t in tools if t.name == "delete_relations"), None)
        
        self.assertIsNotNone(delete_rel_tool)
        self.assertEqual(delete_rel_tool.name, "delete_relations")
        self.assertIn("Delete relationships", delete_rel_tool.description)
        
        # Check schema
        schema = delete_rel_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("source_id", properties)
        self.assertIn("target_id", properties)
        self.assertIn("relationship_type", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("source_id", required)
        self.assertIn("target_id", required)
    
    def test_add_observations_tool_exists(self):
        """Test that add_observations tool exists and has correct schema."""
        tools = get_all_tools()
        add_obs_tool = next((t for t in tools if t.name == "add_observations"), None)
        
        self.assertIsNotNone(add_obs_tool)
        self.assertEqual(add_obs_tool.name, "add_observations")
        self.assertIn("Add observation statements", add_obs_tool.description)
        
        # Check schema
        schema = add_obs_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("entity_id", properties)
        self.assertIn("observation_text", properties)
        self.assertIn("timestamp", properties)
        self.assertIn("source", properties)
        self.assertIn("confidence", properties)
        self.assertIn("tags", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("entity_id", required)
        self.assertIn("observation_text", required)
    
    def test_delete_observations_tool_exists(self):
        """Test that delete_observations tool exists and has correct schema."""
        tools = get_all_tools()
        delete_obs_tool = next((t for t in tools if t.name == "delete_observations"), None)
        
        self.assertIsNotNone(delete_obs_tool)
        self.assertEqual(delete_obs_tool.name, "delete_observations")
        self.assertIn("Delete observation statements", delete_obs_tool.description)
        
        # Check schema
        schema = delete_obs_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
        
        # Check properties
        properties = schema["properties"]
        self.assertIn("entity_id", properties)
        self.assertIn("observation_id", properties)
        self.assertIn("observation_text", properties)
        self.assertIn("source", properties)
        self.assertIn("tags", properties)
        
        # Check required fields
        required = schema["required"]
        self.assertIn("entity_id", required)
    
    
    
    def test_disconnect_neo4j_tool_exists(self):
        """Test that disconnect_neo4j tool exists and has correct schema."""
        tools = get_all_tools()
        disconnect_tool = next((t for t in tools if t.name == "disconnect_neo4j"), None)
        
        self.assertIsNotNone(disconnect_tool)
        self.assertEqual(disconnect_tool.name, "disconnect_neo4j")
        self.assertIn("Disconnect from the Neo4j database", disconnect_tool.description)
        
        # Check schema
        schema = disconnect_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        
        # Disconnect tool should have empty properties
        self.assertEqual(len(schema["properties"]), 0)

    def test_shutdown_server_tool_exists(self):
        """Test that shutdown_server tool exists and has correct schema."""
        tools = get_all_tools()
        shutdown_tool = next((t for t in tools if t.name == "shutdown_server"), None)
        self.assertIsNotNone(shutdown_tool)
        self.assertEqual(shutdown_tool.name, "shutdown_server")
        self.assertIn("Request graceful shutdown", shutdown_tool.description)
        schema = shutdown_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertEqual(len(schema["properties"]), 0)


class TestToolDefinitionsIntegration(unittest.TestCase):
    """Integration tests for tool definitions."""
    
    def test_tool_names_are_unique(self):
        """Test that all tool names are unique."""
        tools = get_all_tools()
        tool_names = [tool.name for tool in tools]
        unique_names = set(tool_names)
        
        self.assertEqual(len(tool_names), len(unique_names), 
                        f"Duplicate tool names found: {[name for name in tool_names if tool_names.count(name) > 1]}")
    
    def test_expected_number_of_tools(self):
        """Test that we have the expected number of tools."""
        tools = get_all_tools()
        expected_tools = [
            "connect_neo4j",
            "run_cypher_query", 
            "find_nodes",
            "search_nodes",
            "create_entities",
            "delete_entities",
            "create_relations",
            "delete_relations",
            "add_observations",
            "delete_observations",
            "disconnect_neo4j",
            "health_check",
            "shutdown_server"
        ]
        
        self.assertEqual(len(tools), len(expected_tools))
        
        actual_tool_names = [tool.name for tool in tools]
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, actual_tool_names, 
                         f"Missing tool: {expected_tool}")
    
    def test_all_tools_have_valid_schemas(self):
        """Test that all tools have valid JSON schemas."""
        tools = get_all_tools()
        
        for tool in tools:
            schema = tool.inputSchema
            
            # Basic schema validation
            self.assertIn("type", schema)
            self.assertEqual(schema["type"], "object")
            self.assertIn("properties", schema)
            self.assertIsInstance(schema["properties"], dict)
            
            # Check that required fields exist in properties
            if "required" in schema:
                for required_field in schema["required"]:
                    self.assertIn(required_field, schema["properties"],
                                 f"Required field '{required_field}' not found in properties for tool '{tool.name}'")
    
    def test_boolean_properties_have_correct_type(self):
        """Test that boolean properties have correct type definition."""
        tools = get_all_tools()
        
        for tool in tools:
            schema = tool.inputSchema
            properties = schema["properties"]
            
            for prop_name, prop_schema in properties.items():
                if prop_schema.get("type") == "boolean":
                    # Boolean properties should have default values
                    self.assertIn("default", prop_schema,
                                 f"Boolean property '{prop_name}' in tool '{tool.name}' should have a default value")
                    self.assertIsInstance(prop_schema["default"], bool)


if __name__ == '__main__':
    unittest.main()