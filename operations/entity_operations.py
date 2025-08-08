"""
Entity operations for the Neo4j MCP server.
Contains create_entities and delete_entities functionality.
"""

import logging
from typing import Dict, Any
from mcp.types import CallToolResult

logger = logging.getLogger(__name__)


class EntityOperations:
    """Handles entity (node) operations."""
    
    def __init__(self, db_operations):
        self.db_operations = db_operations
    
    async def create_entities(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Create memory entities (nodes) in the graph."""
        connection_check = await self.db_operations._check_connection()
        if connection_check:
            return connection_check
        
        try:
            # Validate presence of required arguments with clear errors matching tests
            if "entity_type" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Entity type is required"}], isError=True)
            entity_type = arguments["entity_type"]
            if entity_type == "":
                return CallToolResult(content=[{"type": "text", "text": "Entity type cannot be empty"}], isError=True)
            if "properties" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Properties are required"}], isError=True)
            properties = arguments["properties"]
            if isinstance(properties, dict) and len(properties) == 0:
                return CallToolResult(content=[{"type": "text", "text": "Name or id property is required"}], isError=True)
            labels = arguments.get("labels", [])
            
            # Validate required properties
            from utils import validate_entity_properties
            is_valid, error_msg = validate_entity_properties(properties)
            if not is_valid:
                # Normalize message to test expectation wording
                if "name" in error_msg and "id" in error_msg:
                    error_msg = "Name or id property is required"
                return CallToolResult(
                    content=[{"type": "text", "text": error_msg}],
                    isError=True
                )
            
            # Build labels string
            all_labels = [entity_type] + labels
            label_string = ":".join(all_labels)
            
            # Cypher query (using $properties map parameter)
            query = f"""
            CREATE (n:{label_string} $properties)
            RETURN n
            """
            parameters = {"properties": properties}
            
            # Delegate execution to db_operations.run_query so tests can mock it
            return await self.db_operations.run_query(query, parameters)
                
        except Exception as e:  # noqa: BLE001
            return CallToolResult(
                content=[{"type": "text", "text": f"Error creating entity: {str(e)}"}],
                isError=True
            )
    
    async def delete_entities(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Delete memory entities (nodes) from the graph."""
        connection_check = await self.db_operations._check_connection()
        if connection_check:
            return connection_check
        
        try:
            if "entity_id" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Entity ID is required"}], isError=True)
            entity_id = arguments["entity_id"]
            if entity_id == "":
                return CallToolResult(content=[{"type": "text", "text": "Entity ID cannot be empty"}], isError=True)
            entity_type = arguments.get("entity_type")
            delete_relationships = arguments.get("delete_relationships", True)
            
            if entity_type:
                if delete_relationships:
                    query = """
                    MATCH (n:$entity_type) 
                    WHERE n.name = $entity_id OR n.id = $entity_id OR elementId(n) = $entity_id
                    OPTIONAL MATCH (n)-[r]-()
                    DELETE r, n
                    RETURN count(n) as deleted_count
                    """
                else:
                    query = """
                    MATCH (n:$entity_type) 
                    WHERE n.name = $entity_id OR n.id = $entity_id OR elementId(n) = $entity_id
                    DELETE n
                    RETURN count(n) as deleted_count
                    """
                parameters = {
                    "entity_id": entity_id,
                    "entity_type": entity_type
                }
            else:
                if delete_relationships:
                    query = """
                    MATCH (n) 
                    WHERE n.name = $entity_id OR n.id = $entity_id OR elementId(n) = $entity_id
                    OPTIONAL MATCH (n)-[r]-()
                    DELETE r, n
                    RETURN count(n) as deleted_count
                    """
                else:
                    query = """
                    MATCH (n) 
                    WHERE n.name = $entity_id OR n.id = $entity_id OR elementId(n) = $entity_id
                    DELETE n
                    RETURN count(n) as deleted_count
                    """
                parameters = {
                    "entity_id": entity_id
                }
            
            return await self.db_operations.run_query(query, parameters)
                
        except Exception as e:  # noqa: BLE001
            return CallToolResult(
                content=[{"type": "text", "text": f"Error deleting entity: {str(e)}"}],
                isError=True
            )