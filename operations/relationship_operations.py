"""
Relationship operations for the Neo4j MCP server.
Contains create_relations and delete_relations functionality.
"""

import logging
from typing import Dict, Any
from mcp.types import CallToolResult

logger = logging.getLogger(__name__)


class RelationshipOperations:
    """Handles relationship operations between entities."""
    
    def __init__(self, db_operations):
        self.db_operations = db_operations
    
    async def create_relations(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Create relationships between entities."""
        connection_check = await self.db_operations._check_connection()
        if connection_check:
            return connection_check
        
        try:
            # Validate required arguments with explicit messages
            if "source_id" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Source ID is required"}], isError=True)
            if "target_id" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Target ID is required"}], isError=True)
            if "relationship_type" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Relationship type is required"}], isError=True)
            source_id = arguments["source_id"]
            target_id = arguments["target_id"]
            relationship_type = arguments["relationship_type"]
            properties = arguments.get("properties", {})
            
            if properties:
                props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
                query = f"""
                MATCH (source), (target) 
                WHERE (source.name = $source_id OR source.id = $source_id OR elementId(source) = $source_id)
                AND (target.name = $target_id OR target.id = $target_id OR elementId(target) = $target_id)
                CREATE (source)-[r:{relationship_type} {{{props_str}}}]->(target)
                RETURN r
                """
            else:
                query = f"""
                MATCH (source), (target) 
                WHERE (source.name = $source_id OR source.id = $source_id OR elementId(source) = $source_id)
                AND (target.name = $target_id OR target.id = $target_id OR elementId(target) = $target_id)
                CREATE (source)-[r:{relationship_type}]->(target)
                RETURN r
                """
            
            parameters = {
                "source_id": source_id,
                "target_id": target_id,
                **properties
            }
            
            return await self.db_operations.run_query(query, parameters)
                
        except Exception as e:  # noqa: BLE001
            return CallToolResult(
                content=[{"type": "text", "text": f"Error creating relationship: {str(e)}"}],
                isError=True
            )
    
    async def delete_relations(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Delete relationships between entities."""
        connection_check = await self.db_operations._check_connection()
        if connection_check:
            return connection_check
        
        try:
            if "source_id" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Source ID is required"}], isError=True)
            if "target_id" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Target ID is required"}], isError=True)
            source_id = arguments["source_id"]
            target_id = arguments["target_id"]
            relationship_type = arguments.get("relationship_type")
            
            if relationship_type:
                query = f"""
                MATCH (source)-[r:{relationship_type}]->(target) 
                WHERE (source.name = $source_id OR source.id = $source_id OR elementId(source) = $source_id)
                AND (target.name = $target_id OR target.id = $target_id OR elementId(target) = $target_id)
                DELETE r
                RETURN count(r) as deleted_count
                """
            else:
                query = """
                MATCH (source)-[r]->(target) 
                WHERE (source.name = $source_id OR source.id = $source_id OR elementId(source) = $source_id)
                AND (target.name = $target_id OR target.id = $target_id OR elementId(target) = $target_id)
                DELETE r
                RETURN count(r) as deleted_count
                """
            parameters = {
                "source_id": source_id,
                "target_id": target_id
            }
            
            return await self.db_operations.run_query(query, parameters)
                
        except Exception as e:  # noqa: BLE001
            return CallToolResult(
                content=[{"type": "text", "text": f"Error deleting relationship: {str(e)}"}],
                isError=True
            )