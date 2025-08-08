# Neo4j MCP Server

A bare bones Model Context Protocol (MCP) server for Neo4j integration using AsyncGraphDatabase.

## Features

- Connect to Neo4j database
- Run Cypher queries
- Disconnect from database
- Async/await support
- Health check tool for status & uptime

## Installation

### Quick Setup

Run the setup script for automatic installation:
```bash
python setup.py
```

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make the server executable:
```bash
chmod +x server.py
```

## Connection Options

There are three supported ways to provide Neo4j connection credentials. They are evaluated in this order at startup:

1. Command Line Arguments (highest immediacy)
   - Pass `--neo4j-uri`, `--neo4j-username`, `--neo4j-password` to `server.py`.
   - If all three are present, an eager connection attempt is performed immediately on startup and you receive success/failure feedback.

2. Environment Variables (auto / lazy-eager)
   - Set:
     ```bash
     export NEO4J_URI='neo4j://localhost:7687'
     export NEO4J_USERNAME='neo4j'
     export NEO4J_PASSWORD='your_password'
     ```
   - If command line args are missing, the server loads `.env` (if present) and environment variables. If all three are found, an eager connection is attempted once at startup.

3. Manual Tool Invocation (deferred / dynamic)
   - If neither full CLI nor full env credentials are available at startup, the server starts without a connection and logs that it is awaiting manual connection.
   - Use one of the following tools:
     - `connect_neo4j` – Always attempts a new connection (unconditional). If a connection already exists it will be overwritten only if the internal driver state was cleared; otherwise prefer the manual variant below for explicit control.
     - `manual_connect_neo4j` – Adds safe reconnection semantics:
       - If already connected and `force` is `false` or omitted: skips reconnect and returns a message: *Already connected; skipping reconnect (use force=true to reconnect).* 
       - If already connected and `force=true`: disconnects cleanly first, then reconnects with the supplied credentials.
       - If not connected: performs a normal connect.
   - This is useful for rotating credentials, switching databases, or establishing a connection after sensitive secrets are fetched from a vault mid-session.

### Choosing an Approach
| Scenario | Recommended Method |
|----------|-------------------|
| Local dev with stable creds | Environment variables (.env) |
| One-off script invocation | Command line arguments |
| Need to swap creds at runtime | `manual_connect_neo4j` with `force=true` |
| Unsure at start / delayed secret retrieval | Start without creds, then `manual_connect_neo4j` |

### Notes
- Partial CLI arguments (e.g., only URI) do not trigger eager connect; missing fields are filled from environment if present.
- If after startup you realize credentials are wrong, call `manual_connect_neo4j` with the corrected values and `force=true`.
- Disconnect anytime with `disconnect_neo4j`.

## Configuration

The server supports multiple configuration methods:

### Environment Variables (Recommended)

Set these environment variables for automatic connection:

```bash
export NEO4J_URI='neo4j://localhost:7687'
export NEO4J_USERNAME='neo4j'
export NEO4J_PASSWORD='your_password'
```

When these environment variables are set (and CLI args not fully provided), the server will automatically attempt a connection at startup. If that fails or is incomplete, you can still connect manually via tools.

### Manual Connection (Tools)

If no full credential set is available at startup, connect using:
- `connect_neo4j` (always attempts) or
- `manual_connect_neo4j` (skips if already connected unless `force=true`)

## Usage

### Testing

Test the comprehensive MCP server functionality (no Neo4j required for basic tests):
```bash
python test_comprehensive.py
```



### Running the Server

The server can be run directly with optional Neo4j connection parameters:

```bash
# Run without connection parameters (uses environment variables or manual connection)
python server.py

# Run with connection parameters (eager connect)
python server.py --neo4j-uri neo4j://localhost:7687 --neo4j-username neo4j --neo4j-password your_password

# Run with some parameters (others will use environment variables)
python server.py --neo4j-uri neo4j://localhost:7687 --neo4j-username neo4j
```

#### Command Line Options

- `--neo4j-uri`: Neo4j connection URI (e.g., `neo4j://localhost:7687`)
- `--neo4j-username`: Neo4j username
- `--neo4j-password`: Neo4j password

When connection parameters are provided via command line, they take precedence over environment variables. If not all parameters are provided, the server will fall back to environment variables for the missing ones.

### Available Tools

The server provides thirteen main tools:

1. **connect_neo4j**
   - Connects to a Neo4j database
   - Parameters:
     - `uri`: Neo4j connection URI (e.g., `neo4j://localhost:7687`)
     - `username`: Neo4j username
     - `password`: Neo4j password

1a. **manual_connect_neo4j**
   - Manually (re)connect with safe force semantics
   - Parameters:
     - `uri`, `username`, `password` (same as above)
     - `force` (boolean, optional, default false)

2. **run_cypher_query**
   - Executes Cypher queries against the connected database
   - Parameters:
     - `query`: Cypher query to execute
     - `parameters`: Optional query parameters (default: {})

3. **find_nodes**
   - Find nodes by name (exact or partial match)
   - Parameters:
     - `name`: Name to search for
     - `exact_match`: Whether to use exact matching (default: false)
     - `case_sensitive`: Whether the search is case sensitive (default: false)

4. **search_nodes**
   - Search nodes by string in any property
   - Parameters:
     - `search_string`: String to search for in node properties
     - `property_name`: Specific property to search in (optional, searches all if not specified)
     - `case_sensitive`: Whether the search is case sensitive (default: false)

5. **create_entities**
   - Create memory entities (nodes) in the graph
   - Parameters:
     - `entity_type`: Type/category of entity (e.g., 'Person', 'Place', 'Concept')
     - `properties`: Properties of the entity (must include 'name' or 'id')
     - `labels`: Additional labels for the entity (optional)

6. **delete_entities**
   - Delete memory entities (nodes) from the graph
   - Parameters:
     - `entity_id`: Entity identifier (name, id, or internal Neo4j ID)
     - `entity_type`: Type/category of entity to filter by (optional)
     - `delete_relationships`: Whether to also delete relationships (default: true)

7. **create_relations**
   - Create relationships between entities
   - Parameters:
     - `source_id`: Source entity identifier
     - `target_id`: Target entity identifier
     - `relationship_type`: Type of relationship (e.g., 'KNOWS', 'LIVES_IN', 'WORKS_FOR')
     - `properties`: Properties of the relationship (optional)

8. **delete_relations**
   - Delete relationships between entities
   - Parameters:
     - `source_id`: Source entity identifier
     - `target_id`: Target entity identifier
     - `relationship_type`: Specific relationship type to delete (optional, deletes all if not specified)

9. **add_observations**
   - Add observation statements to entities
   - Parameters:
     - `entity_id`: Target entity identifier
     - `observation_text`: The observation statement to add
     - `timestamp`: Timestamp for the observation (optional, uses current time if not provided)
     - `source`: Source of the observation (optional)
     - `confidence`: Confidence level of the observation (0.0 to 1.0, optional)
     - `tags`: Tags for categorizing the observation (optional)

10. **delete_observations**
    - Delete observation statements from entities
    - Parameters:
      - `entity_id`: Target entity identifier
      - `observation_id`: Specific observation ID to delete (optional, deletes all if not specified)
      - `observation_text`: Observation text to match for deletion (optional)
      - `source`: Source filter for deletion (optional)
      - `tags`: Tags filter for deletion (optional)

11. **disconnect_neo4j**
    - Disconnects from the Neo4j database
    - No parameters required

12. **health_check**
    - Returns server health including: connection state, server version, sanitized Neo4j URI, uptime (seconds)
    - No parameters required

### Example Usage

1. Connect to Neo4j:
```json
{
  "name": "connect_neo4j",
  "arguments": {
    "uri": "neo4j://localhost:7687",
    "username": "neo4j",
    "password": "password"
  }
}
```

1a. Manual connect with force reconnect:
```json
{
  "name": "manual_connect_neo4j",
  "arguments": {
    "uri": "neo4j://localhost:7687",
    "username": "neo4j",
    "password": "password",
    "force": true
  }
}
```

2. Run a query:
```json
{
  "name": "run_cypher_query",
  "arguments": {
    "query": "MATCH (n) RETURN n LIMIT 5",
    "parameters": {}
  }
}
```

3. Health check:
```json
{
  "name": "health_check",
  "arguments": {}
}
```

3. Find nodes by name:
```json
{
  "name": "find_nodes",
  "arguments": {
    "name": "Alice Johnson",
    "exact_match": true,
    "case_sensitive": false
  }
}
```

4. Search nodes in all properties:
```json
{
  "name": "search_nodes",
  "arguments": {
    "search_string": "New York",
    "case_sensitive": false
  }
}
```

5. Search nodes in specific property:
```json
{
  "name": "search_nodes",
  "arguments": {
    "search_string": "Johnson",
    "property_name": "name",
    "case_sensitive": false
  }
}
```

6. Create an entity:
```json
{
  "name": "create_entities",
  "arguments": {
    "entity_type": "Person",
    "properties": {
      "name": "John Doe",
      "age": 30,
      "occupation": "Software Engineer"
    },
    "labels": ["Employee", "Developer"]
  }
}
```

7. Create a relationship:
```json
{
  "name": "create_relations",
  "arguments": {
    "source_id": "John Doe",
    "target_id": "TechCorp",
    "relationship_type": "WORKS_FOR",
    "properties": {
      "start_date": "2020-01-15",
      "position": "Senior Engineer"
    }
  }
}
```

8. Delete a relationship:
```json
{
  "name": "delete_relations",
  "arguments": {
    "source_id": "John Doe",
    "target_id": "Jane Smith",
    "relationship_type": "KNOWS"
  }
}
```

9. Delete an entity:
```json
{
  "name": "delete_entities",
  "arguments": {
    "entity_id": "John Doe",
    "entity_type": "Person",
    "delete_relationships": true
  }
}
```

10. Add an observation:
```json
{
  "name": "add_observations",
  "arguments": {
    "entity_id": "Alice Johnson",
    "observation_text": "Alice is conducting research on neural networks",
    "timestamp": "2024-01-15T10:30:00",
    "source": "Lab Assistant",
    "confidence": 0.9,
    "tags": ["research", "neural-networks", "ongoing"]
  }
}
```

11. Delete observations:
```json
{
  "name": "delete_observations",
  "arguments": {
    "entity_id": "Alice Johnson",
    "tags": ["work-hours"]
  }
}
```

12. Disconnect:
```json
{
  "name": "disconnect_neo4j",
  "arguments": {}
}
```

13. Health check:
```json
{
  "name": "health_check",
  "arguments": {}
}
```

## Configuration

The server uses stdio for communication and can be integrated with any MCP-compatible client.

## Error Handling

The server includes comprehensive error handling for:
- Connection failures
- Query execution errors
- Invalid tool calls
- Disconnection issues

All errors are returned as structured responses with error flags.

## Troubleshooting

### NumPy Compatibility Issues

If you encounter NumPy compatibility errors when importing Neo4j, try this solution:

**Manual Fix**
```bash
pip install --force-reinstall "numpy<2.0.0"
pip install --force-reinstall "pandas<2.0.0"
pip install -r requirements.txt
```

The issue occurs because NumPy 2.x is incompatible with some dependencies that were compiled with NumPy 1.x.

### MCP Library Issues

If you have issues with the MCP library, ensure you have the latest version:

```bash
pip install --upgrade mcp
```

### Neo4j Connection Issues

- Ensure Neo4j is running and accessible
- Check your connection URI format: `neo4j://hostname:port`
- Verify username and password are correct
- For Neo4j 5.0+, you may need to change the default password on first startup