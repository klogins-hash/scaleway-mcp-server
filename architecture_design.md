# Scaleway MCP Connector - Architecture Design

## Overview

The Scaleway MCP Connector is a Model Context Protocol server that enables AI assistants (like Manus) to interact with Scaleway cloud infrastructure programmatically. It provides tools for managing instances, storage, databases, networking, and Kubernetes clusters.

## Architecture Components

### 1. Core Server (FastMCP)
- **Framework**: FastMCP (MCP Python SDK)
- **Transport**: STDIO (standard input/output)
- **Python Version**: 3.1your_access_key_here+
- **Async Support**: Full async/await implementation

### 2. Scaleway Client Manager
- **Purpose**: Initialize and manage Scaleway API clients
- **Credentials**: Load from environment variables
- **APIs Supported**:
  - Instance API (compute)
  - VPC API (networking)
  - K8S API (Kubernetes)
  - Registry API (container registry)
  - Object Storage (S3-compatible)

### 3. Tool Categories

#### Instance Management Tools
- `list_instances`: List all instances in a zone/region
- `create_instance`: Create a new compute instance
- `get_instance`: Get details of a specific instance
- `start_instance`: Start a stopped instance
- `stop_instance`: Stop a running instance
- `delete_instance`: Delete an instance

#### Storage Tools
- `list_buckets`: List all object storage buckets
- `create_bucket`: Create a new bucket
- `list_objects`: List objects in a bucket
- `upload_object`: Upload an object to a bucket
- `download_object`: Download an object from a bucket
- `delete_object`: Delete an object

#### Network Tools
- `list_private_networks`: List private networks
- `create_private_network`: Create a new private network
- `attach_instance_to_network`: Attach instance to private network

#### Kubernetes Tools
- `list_clusters`: List Kubernetes clusters
- `create_cluster`: Create a new Kubernetes cluster
- `get_cluster_kubeconfig`: Get kubeconfig for a cluster
- `delete_cluster`: Delete a Kubernetes cluster

#### Database Tools
- `list_databases`: List managed database instances
- `create_database`: Create a new database instance
- `get_database`: Get database details

## Configuration

### Environment Variables
```bash
SCW_ACCESS_KEY=<access_key>
SCW_SECRET_KEY=<secret_key>
SCW_PROJECT_ID=<project_id>
SCW_ORGANIZATION_ID=<organization_id>
SCW_DEFAULT_REGION=fr-par
SCW_DEFAULT_ZONE=fr-par-1
```

### Credential Loading Priority
1. Environment variables (primary)
2. Fallback to default values (for testing only)
3. Error if no credentials found

## Error Handling Strategy

### API Errors
- Catch Scaleway API exceptions
- Return user-friendly error messages
- Log errors to stderr (not stdout)

### Validation
- Validate required parameters before API calls
- Check credential availability on startup
- Validate region/zone parameters

### Async Error Handling
- Use try/except blocks in all async functions
- Graceful degradation when services unavailable
- Timeout handling for long-running operations

## Logging Strategy

### Constraints
- **NEVER** use `print()` (corrupts STDIO transport)
- Use Python `logging` module
- Log to stderr only
- Log levels: DEBUG, INFO, WARNING, ERROR

### Log Format
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
```

## File Structure

```
scaleway-mcp-server/
├── pyproject.toml           # Project dependencies
├── README.md                # Documentation
├── scaleway_server.py       # Main server implementation
├── .env.example             # Example environment variables
└── tests/                   # Test files (optional)
    └── test_server.py
```

## Tool Response Format

### Success Response
```json
{
  "status": "success",
  "data": {
    "instance_id": "xxx",
    "name": "my-instance",
    "state": "running"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Failed to create instance: Invalid instance type"
}
```

## Security Considerations

### Credential Management
- Never hardcode credentials
- Use environment variables exclusively
- Support for Scaleway credential files (future)

### API Key Permissions
- Require minimum necessary permissions
- Document required IAM permissions
- Support for scoped API keys

### Data Privacy
- No logging of sensitive data
- Sanitize error messages
- Secure credential storage recommendations

## Integration with Manus

### MCP Configuration
Users will configure the server in their Manus MCP settings:

```json
{
  "mcpServers": {
    "scaleway": {
      "command": "uv",
      "args": ["run", "scaleway_server.py"],
      "env": {
        "SCW_ACCESS_KEY": "SCW7JHKD4NQXX6YWY5A4",
        "SCW_SECRET_KEY": "eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34",
        "SCW_PROJECT_ID": "b6c2c4f2-4697-4927-958your_access_key_here-143bf8c3f588",
        "SCW_ORGANIZATION_ID": "c5d299b8-8462-4your_access_key_herefb-b5ae-32a88your_access_key_here8bf394",
        "SCW_DEFAULT_REGION": "fr-par",
        "SCW_DEFAULT_ZONE": "fr-par-1"
      }
    }
  }
}
```

### Usage in Manus
Once configured, users can interact with Scaleway through natural language:
- "List all my Scaleway instances"
- "Create a new instance in Paris zone"
- "Show me my Kubernetes clusters"
- "Upload this file to my S3 bucket"

## Performance Considerations

### Async Operations
- All API calls use async/await
- Concurrent operations where possible
- Timeout configuration for long operations

### Caching
- Cache instance lists for short periods
- Invalidate cache on mutations
- Configurable cache TTL

### Rate Limiting
- Respect Scaleway API rate limits
- Implement exponential backoff
- Queue requests if needed

## Future Enhancements

### Phase 2 Features
- Support for more Scaleway services (Functions, Serverless)
- Batch operations (create multiple instances)
- Resource monitoring and alerts
- Cost estimation tools

### Advanced Features
- Terraform integration
- Infrastructure as Code generation
- Multi-region operations
- Advanced networking (Load Balancers, DNS)

## Testing Strategy

### Unit Tests
- Test each tool independently
- Mock Scaleway API responses
- Validate error handling

### Integration Tests
- Test with real Scaleway API (sandbox)
- Validate credential loading
- Test MCP protocol compliance

### Manual Testing
- Test with MCP Inspector
- Test with Manus integration
- Validate all tool responses
