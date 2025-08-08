"""
Tool definitions for the Neo4j MCP server.
Contains all tool schemas and metadata.
"""

from mcp.types import Tool
from typing import List


def get_all_tools() -> List[Tool]:
    """Get all available tools for the Neo4j MCP server."""
    return [
        Tool(
            name="connect_neo4j",
            description="Connect to a Neo4j database (or reconnect). Supports optional forced reconnection if already connected.",
            inputSchema={
                "type": "object",
                "properties": {
                    "uri": {
                        "type": "string",
                        "description": "Neo4j connection URI (e.g., neo4j://localhost:7687). Can sometimes be found in the environment variable NEO4J_URI."
                    },
                    "username": {
                        "type": "string",
                        "description": "Neo4j username, can sometimes be found in the environment variable NEO4J_USERNAME."
                    },
                    "password": {
                        "type": "string",
                        "description": "Neo4j password, can sometimes be found in the environment variable NEO4J_PASSWORD.\t"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force reconnect even if a connection already exists (default false)",
                        "default": False
                    }
                },
                "required": ["uri", "username", "password"]
            }
        ),
        Tool(
            name="run_cypher_query",
            description="Run a Cypher query against the connected Neo4j database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Cypher query to execute"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Query parameters (optional)",
                        "default": {}
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="find_nodes",
            description="Find nodes by name (exact or partial match)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to search for"
                    },
                    "exact_match": {
                        "type": "boolean",
                        "description": "Whether to use exact matching (default: false)",
                        "default": False
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether the search is case sensitive (default: false)",
                        "default": False
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="search_nodes",
            description="Search nodes by string in any property",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_string": {
                        "type": "string",
                        "description": "String to search for in node properties"
                    },
                    "property_name": {
                        "type": "string",
                        "description": "Specific property to search in (optional, searches all if not specified)"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether the search is case sensitive (default: false)",
                        "default": False
                    }
                },
                "required": ["search_string"]
            }
        ),
        Tool(
            name="create_entities",
            description="Create memory entities (nodes) in the graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "description": "Type/category of entity (e.g., 'Person', 'Place', 'Concept')"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Properties of the entity (must include 'name' or 'id')"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional labels for the entity (optional)"
                    }
                },
                "required": ["entity_type", "properties"]
            }
        ),
        Tool(
            name="delete_entities",
            description="Delete memory entities (nodes) from the graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity identifier (name, id, or internal Neo4j ID)"
                    },
                    "entity_type": {
                        "type": "string",
                        "description": "Type/category of entity to filter by (optional)"
                    },
                    "delete_relationships": {
                        "type": "boolean",
                        "description": "Whether to also delete relationships (default: true)",
                        "default": True
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="create_relations",
            description="Create relationships between entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "Source entity identifier"
                    },
                    "target_id": {
                        "type": "string",
                        "description": "Target entity identifier"
                    },
                    "relationship_type": {
                        "type": "string",
                        "description": "Type of relationship (e.g., 'KNOWS', 'LIVES_IN', 'WORKS_FOR')"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Properties of the relationship (optional)"
                    }
                },
                "required": ["source_id", "target_id", "relationship_type"]
            }
        ),
        Tool(
            name="delete_relations",
            description="Delete relationships between entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "Source entity identifier"
                    },
                    "target_id": {
                        "type": "string",
                        "description": "Target entity identifier"
                    },
                    "relationship_type": {
                        "type": "string",
                        "description": "Specific relationship type to delete (optional, deletes all if not specified)"
                    }
                },
                "required": ["source_id", "target_id"]
            }
        ),
        Tool(
            name="add_observations",
            description="Add observation statements to entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Target entity identifier"
                    },
                    "observation_text": {
                        "type": "string",
                        "description": "The observation statement to add"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Timestamp for the observation (optional, uses current time if not provided)"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source of the observation (optional)"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence level of the observation (0.0 to 1.0, optional)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorizing the observation (optional)"
                    }
                },
                "required": ["entity_id", "observation_text"]
            }
        ),
        Tool(
            name="delete_observations",
            description="Delete observation statements from entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Target entity identifier"
                    },
                    "observation_id": {
                        "type": "string",
                        "description": "Specific observation ID to delete (optional, deletes all if not specified)"
                    },
                    "observation_text": {
                        "type": "string",
                        "description": "Observation text to match for deletion (optional)"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source filter for deletion (optional)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags filter for deletion (optional)"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="disconnect_neo4j",
            description="Disconnect from the Neo4j database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="health_check",
            description="Return server health status including connection state, server version, sanitized Neo4j URI and uptime.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="shutdown_server",
            description="Request graceful shutdown of the server (closes connection and stops event loop).",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]