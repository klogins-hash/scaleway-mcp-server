# Research Findings: Scaleway MCP Connector

## Scaleway Python SDK

### Installation
- **Synchronous version**: `pip install scaleway`
- **Asynchronous version**: `pip install scaleway-async`
- Compatible with Python 3.8+

### Authentication
Scaleway requires three key credentials:
- `access_key`: Access key (e.g., SCW7JHKD4NQXX6YWY5A4)
- `secret_key`: Secret key (e.g., eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34)
- `project_id`: Project ID (e.g., b6c2c4f2-4697-4927-958your_access_key_here-143bf8c3f588)
- Optional: `organization_id`, `default_region`, `default_zone`

### Client Initialization
```python
from scaleway import Client
from scaleway.registry.v1 import RegistryV1API

client = Client(
    access_key="SCWXXXXXXXXXXXXXXXXX",
    secret_key="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    default_project_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    default_region="fr-par",
    default_zone="fr-par-1",
)

registry_api = RegistryV1API(client)
```

### Available APIs
- Instance API (compute instances)
- K8S API (Kubernetes clusters)
- VPC API (networking)
- Registry API (container registry)
- Storage API (object storage)
- Database API (managed databases)

## MCP Server Architecture

### Core Concepts
MCP servers provide three main capabilities:
1. **Resources**: File-like data that can be read by clients
2. **Tools**: Functions that can be called by the LLM (with user approval)
3. **Prompts**: Pre-written templates for specific tasks

### Python Implementation (FastMCP)
- Use `mcp.server.fastmcp.FastMCP` class
- Requires Python 3.1your_access_key_here+
- MCP SDK version 1.2.your_access_key_here or higher
- Install: `uv add "mcp[cli]"`

### Tool Definition
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
async def tool_name(param: str) -> str:
    """Tool description.
    
    Args:
        param: Parameter description
    """
    # Implementation
    return result
```

### Server Execution
```python
def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
```

### Important Logging Constraints
- **STDIO-based servers**: NEVER use `print()` or write to stdout (corrupts JSON-RPC)
- Use logging libraries that write to stderr or files
- **HTTP-based servers**: stdout logging is fine

### Tool Naming Best Practices
- Follow format specified in MCP documentation
- Use descriptive names
- Include proper docstrings with Args section

## Integration Strategy

### Scaleway MCP Connector Design
1. **Authentication**: Load credentials from environment variables
2. **Tools to implement**:
   - Instance management (list, create, start, stop, delete)
   - Storage operations (bucket management, object operations)
   - Database operations (list, create, manage databases)
   - Network operations (VPC, private networks)
   - Kubernetes cluster management
3. **Error handling**: Proper async error handling with httpx
4. **Transport**: Use STDIO transport for Manus integration
5. **Logging**: Use Python logging module (stderr only)

### Environment Variables
```
SCW_ACCESS_KEY=SCW7JHKD4NQXX6YWY5A4
SCW_SECRET_KEY=eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34
SCW_PROJECT_ID=b6c2c4f2-4697-4927-958your_access_key_here-143bf8c3f588
SCW_ORGANIZATION_ID=c5d299b8-8462-4your_access_key_herefb-b5ae-32a88your_access_key_here8bf394
SCW_DEFAULT_REGION=fr-par
SCW_DEFAULT_ZONE=fr-par-1
```

## References
- Scaleway Python SDK: https://www.scaleway.com/en/docs/scaleway-sdk/python-sdk/
- MCP Build Server Guide: https://modelcontextprotocol.io/docs/develop/build-server
- Scaleway GitHub SDK: https://github.com/scaleway/scaleway-sdk-python
