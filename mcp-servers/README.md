# Databricks MCP Servers

**Model Context Protocol (MCP) servers for Databricks operations.**

This package provides MCP servers that enable agents to interact with Databricks infrastructure:
- SQL Warehouse operations (queries, table creation)
- Unity Catalog operations (model/prompt registry)
- Lakebase operations (vector embeddings, similarity search)

## Standalone Package

This is designed as a **standalone, reusable package** that can be:
- Used in this project (monorepo)
- Extracted to a separate repository
- Shared across multiple agent projects
- Deployed as independent services

## MCP Servers Included

### 1. Databricks SQL (`databricks-sql/`)
Operations on SQL Warehouses and Delta tables.

**Tools:**
- `create_table` - Create Delta tables in Unity Catalog
- `query_table` - Execute SQL queries
- `insert_data` - Insert data into tables
- `list_tables` - List tables in catalog/schema

### 2. Unity Catalog (`unity-catalog/`)
Operations on Unity Catalog (model/prompt registry).

**Tools:**
- `register_model` - Register ML models in UC
- `register_prompt` - Store prompts in UC
- `get_schema` - Retrieve schema definitions
- `list_models` - List registered models

### 3. Lakebase (`lakebase/`)
Vector store operations for agent memory.

**Tools:**
- `store_embedding` - Store vector embeddings
- `similarity_search` - Vector similarity search
- `get_context` - Retrieve merchant/customer context
- `store_conversation` - Store agent conversation history

## Installation

### As Part of Monorepo
```bash
# From project root
pip install -e mcp-servers/
```

### As Standalone Package (After Extraction)
```bash
pip install databricks-mcp-servers
```

## Configuration

Create `.env` file with Databricks credentials:

```bash
# Databricks connection (from Terraform outputs)
DATABRICKS_HOST=your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...
DATABRICKS_WAREHOUSE_ID=abc123def456
DATABRICKS_CATALOG=fraud_detection

# Optional: Lakebase
LAKEBASE_ENDPOINT=https://lakebase.your-workspace.com
```

## Running MCP Servers

### Option 1: As Subprocess (Development)
```bash
# Run individual server
python databricks-sql/server.py

# Run all servers
./run_all_servers.sh
```

### Option 2: As HTTP Services (Production)
```bash
# Using Docker Compose
docker-compose up

# Services available at:
# - http://localhost:3001 (databricks-sql)
# - http://localhost:3002 (unity-catalog)
# - http://localhost:3003 (lakebase)
```

## Usage from Agents

Agents connect via MCP client (NOT direct imports!):

```python
from mcp import MCPClient

# Connect to MCP server
client = MCPClient(url="http://localhost:3001")

# Call tool
result = await client.call_tool(
    server="databricks-sql",
    tool="query_table",
    arguments={"query": "SELECT * FROM fraud_detection.transactions"}
)
```

**Key:** No direct imports from agent code! MCP servers are accessed via API.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .
```

## Architecture

```
mcp-servers/                        # Standalone package
├── databricks-sql/                 # SQL Warehouse MCP server
│   ├── server.py                   # MCP server implementation
│   └── tools/                      # Tool implementations
├── unity-catalog/                  # Unity Catalog MCP server
├── lakebase/                       # Lakebase MCP server
└── shared/                         # Shared utilities (MCP-specific only)
    ├── auth.py                     # Databricks authentication
    └── schemas.py                  # MCP tool schemas
```

**No dependencies on parent project!** This package is self-contained.

## Deployment

### Local Development
```bash
python databricks-sql/server.py
```

### Docker
```bash
docker build -t databricks-mcp-servers .
docker run -p 3001:3000 databricks-mcp-servers
```

### Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

## Extraction to Separate Repo

When ready to extract to separate repository:

```bash
# From parent project
git subtree split --prefix=mcp-servers -b mcp-extract

# Create new repo
mkdir ../databricks-mcp-servers
cd ../databricks-mcp-servers
git init
git pull ../parent-project mcp-extract
```

**No code changes needed!** Package is already structured for standalone use.

## License

MIT

