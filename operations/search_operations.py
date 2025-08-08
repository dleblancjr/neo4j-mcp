"""
Search operations for the Neo4j MCP server.
Contains find_nodes and search_nodes functionality.
"""

import logging
from typing import Dict, Any
from mcp.types import CallToolResult

logger = logging.getLogger(__name__)


class SearchOperations:
    """Handles search operations for nodes."""
    
    def __init__(self, db_operations):
        self.db_operations = db_operations
    
    async def find_nodes(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Find nodes by name (exact or partial match)."""
        connection_check = await self.db_operations._check_connection()
        if connection_check:
            return connection_check
        
        try:
            if "name" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Name parameter is required"}], isError=True)
            name = arguments["name"]
            if name == "":
                return CallToolResult(content=[{"type": "text", "text": "Name cannot be empty"}], isError=True)
            exact_match = arguments.get("exact_match", False)
            case_sensitive = arguments.get("case_sensitive", False)
            
            if exact_match:
                if case_sensitive:
                    query = """
                    MATCH (n) 
                    WHERE n.name = $name
                    RETURN n
                    LIMIT 100
                    """
                else:
                    query = """
                    MATCH (n) 
                    WHERE toLower(n.name) = toLower($name)
                    RETURN n
                    LIMIT 100
                    """
            else:
                if case_sensitive:
                    query = """
                    MATCH (n) 
                    WHERE n.name CONTAINS $name
                    RETURN n
                    LIMIT 100
                    """
                else:
                    query = """
                    MATCH (n) 
                    WHERE toLower(n.name) CONTAINS toLower($name)
                    RETURN n
                    LIMIT 100
                    """
            
            parameters = {"name": name}
            return await self.db_operations.run_query(query, parameters)
                
        except Exception as e:  # noqa: BLE001
            return CallToolResult(
                content=[{"type": "text", "text": f"Error finding nodes: {str(e)}"}],
                isError=True
            )
    
    async def search_nodes(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Search nodes by string in any property."""
        connection_check = await self.db_operations._check_connection()
        if connection_check:
            return connection_check
        
        try:
            if "search_string" not in arguments:
                return CallToolResult(content=[{"type": "text", "text": "Search string parameter is required"}], isError=True)
            search_string = arguments["search_string"]
            if search_string == "":
                return CallToolResult(content=[{"type": "text", "text": "Search string cannot be empty"}], isError=True)
            property_name = arguments.get("property_name")
            case_sensitive = arguments.get("case_sensitive", False)
            
            if property_name:
                if case_sensitive:
                    query = f"""
                    MATCH (n) 
                    WHERE n.{property_name} CONTAINS $search_string
                    RETURN n
                    LIMIT 100
                    """
                else:
                    query = f"""
                    MATCH (n) 
                    WHERE toLower(n.{property_name}) CONTAINS toLower($search_string)
                    RETURN n
                    LIMIT 100
                    """
            else:
                if case_sensitive:
                    query = """
                    MATCH (n) 
                    WHERE (n.name CONTAINS $search_string) OR (n.city CONTAINS $search_string) OR (n.occupation CONTAINS $search_string)
                    RETURN n
                    LIMIT 100
                    """
                else:
                    query = """
                    MATCH (n) 
                    WHERE (toLower(n.name) CONTAINS toLower($search_string)) OR (toLower(n.city) CONTAINS toLower($search_string)) OR (toLower(n.occupation) CONTAINS toLower($search_string))
                    RETURN n
                    LIMIT 100
                    """
            parameters = {"search_string": search_string}
            return await self.db_operations.run_query(query, parameters)
                
        except Exception as e:  # noqa: BLE001
            return CallToolResult(
                content=[{"type": "text", "text": f"Error searching nodes: {str(e)}"}],
                isError=True
            )