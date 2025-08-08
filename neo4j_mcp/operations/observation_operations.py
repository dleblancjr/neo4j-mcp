"""
Observation operations for the Neo4j MCP server.
Contains add_observations and delete_observations functionality.
"""

import logging
from typing import Dict, Any
from mcp.types import CallToolResult

logger = logging.getLogger(__name__)


class ObservationOperations:
    """Handles observation operations for entities."""
    
    def __init__(self, db_operations):
        self.db_operations = db_operations
    
    async def add_observations(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Add observation statements to entities."""
        connection_check = await self.db_operations._check_connection()
        if connection_check:
            return connection_check
        
        try:
            # Validate required arguments and empties
            if "entity_id" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Entity ID is required"}], isError=True)
            entity_id = arguments["entity_id"]
            if entity_id == "":
                return CallToolResult(content=[{"type": "text", "text": "Entity ID cannot be empty"}], isError=True)
            if "observation_text" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Observation text is required"}], isError=True)
            observation_text = arguments["observation_text"]
            if observation_text == "":
                return CallToolResult(content=[{"type": "text", "text": "Observation text cannot be empty"}], isError=True)
            timestamp = arguments.get("timestamp")
            source = arguments.get("source")
            confidence = arguments.get("confidence")
            tags = arguments.get("tags", [])
            
            # Generate timestamp if not provided
            if not timestamp:
                from datetime import datetime
                timestamp = datetime.now().isoformat()
            
            # Validate confidence if provided
            from ..utils import validate_confidence
            is_valid, error_msg = validate_confidence(confidence)
            if not is_valid:
                return CallToolResult(
                    content=[{"type": "text", "text": error_msg}],
                    isError=True
                )
            
            query = """
            MATCH (entity) 
            WHERE entity.name = $entity_id OR entity.id = $entity_id OR elementId(entity) = $entity_id
            CREATE (entity)-[r:HAS_OBSERVATION]->(obs:Observation {
                text: $observation_text,
                timestamp: $timestamp,
                source: $source,
                confidence: $confidence,
                tags: $tags
            })
            RETURN obs
            """
            
            parameters = {
                "entity_id": entity_id,
                "observation_text": observation_text,
                "timestamp": timestamp,
                "source": source,
                "confidence": confidence,
                "tags": tags
            }
            
            return await self.db_operations.run_query(query, parameters)
                
        except Exception as e:  # noqa: BLE001
            return CallToolResult(
                content=[{"type": "text", "text": f"Error adding observation: {str(e)}"}],
                isError=True
            )
    
    async def delete_observations(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Delete observation statements from entities."""
        connection_check = await self.db_operations._check_connection()
        if connection_check:
            return connection_check
        
        try:
            if "entity_id" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Entity ID is required"}], isError=True)
            entity_id = arguments["entity_id"]
            if entity_id == "":
                return CallToolResult(content=[{"type": "text", "text": "Entity ID cannot be empty"}], isError=True)
            observation_id = arguments.get("observation_id")
            observation_text = arguments.get("observation_text")
            source = arguments.get("source")
            tags = arguments.get("tags", [])
            
            if observation_id:
                query = """
                MATCH (entity)-[r:HAS_OBSERVATION]->(obs:Observation) 
                WHERE (entity.name = $entity_id OR entity.id = $entity_id OR elementId(entity) = $entity_id)
                AND elementId(obs) = $observation_id
                DELETE r, obs
                RETURN count(obs) as deleted_count
                """
                parameters = {
                    "entity_id": entity_id,
                    "observation_id": observation_id
                }
            elif observation_text:
                query = """
                MATCH (entity)-[r:HAS_OBSERVATION]->(obs:Observation) 
                WHERE (entity.name = $entity_id OR entity.id = $entity_id OR elementId(entity) = $entity_id)
                AND obs.text CONTAINS $observation_text
                DELETE r, obs
                RETURN count(obs) as deleted_count
                """
                parameters = {
                    "entity_id": entity_id,
                    "observation_text": observation_text
                }
            elif source:
                query = """
                MATCH (entity)-[r:HAS_OBSERVATION]->(obs:Observation) 
                WHERE (entity.name = $entity_id OR entity.id = $entity_id OR elementId(entity) = $entity_id)
                AND obs.source = $source
                DELETE r, obs
                RETURN count(obs) as deleted_count
                """
                parameters = {
                    "entity_id": entity_id,
                    "source": source
                }
            elif tags:
                query = """
                MATCH (entity)-[r:HAS_OBSERVATION]->(obs:Observation) 
                WHERE (entity.name = $entity_id OR entity.id = $entity_id OR elementId(entity) = $entity_id)
                AND ANY(tag IN $tags WHERE tag IN obs.tags)
                DELETE r, obs
                RETURN count(obs) as deleted_count
                """
                parameters = {
                    "entity_id": entity_id,
                    "tags": tags
                }
            else:
                query = """
                MATCH (entity)-[r:HAS_OBSERVATION]->(obs:Observation) 
                WHERE (entity.name = $entity_id OR entity.id = $entity_id OR elementId(entity) = $entity_id)
                DELETE r, obs
                RETURN count(obs) as deleted_count
                """
                parameters = {
                    "entity_id": entity_id
                }
            
            return await self.db_operations.run_query(query, parameters)
                
        except Exception as e:  # noqa: BLE001
            return CallToolResult(
                content=[{"type": "text", "text": f"Error deleting observations: {str(e)}"}],
                isError=True
            )