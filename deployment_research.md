# Deployment Research: Scaleway Serverless Containers + MCP HTTP

## Scaleway Serverless Containers

### Key Features
- Deploy containerized applications without managing infrastructure
- Supports any public container registry (Scaleway Registry, Docker Hub, etc.)
- Auto-scaling based on request concurrency, CPU, or RAM
- Environment variables and secrets support
- HTTP-based access with custom ports
- Pay-per-use pricing model

### Deployment Requirements
1. Container image pushed to a registry
2. Container must listen on HTTP port (configurable via $PORT env var)
3. Environment variables for configuration
4. Dockerfile to build the image

### Configuration Options
- CPU and memory allocation
- Auto-scaling parameters (min/max instances)
- Environment variables and secrets
- Health checks
- Request timeout settings

## MCP Transport Options

### STDIO Transport (Current Implementation)
- Communication via stdin/stdout
- Client launches server as subprocess
- Messages delimited by newlines
- **Cannot be used for remote/HTTP deployment**

### Streamable HTTP Transport (Required for Serverless)
- Server operates as independent HTTP process
- Supports multiple client connections
- Uses HTTP POST for client-to-server messages
- Uses HTTP GET + SSE for server-to-client messages
- Session management via `Mcp-Session-Id` header
- **Required for Scaleway Serverless Containers**

### HTTP Transport Implementation
1. Server must provide HTTP endpoint (e.g., `/mcp`)
2. Accept POST requests with JSON-RPC messages
3. Return responses as JSON or SSE streams
4. Support GET requests for SSE streaming
5. Implement proper CORS and Origin validation

## Implementation Strategy

### Option 1: FastMCP with HTTP Transport
- FastMCP primarily supports STDIO
- Would need custom HTTP wrapper
- More complex implementation

### Option 2: Use FastAPI + MCP SDK
- Create FastAPI application
- Implement MCP protocol manually
- Handle HTTP POST/GET endpoints
- Manage SSE streaming
- More control but more code

### Option 3: Use MCP HTTP Framework
- Look for existing HTTP MCP server frameworks
- Minimal custom code
- May have limitations

## Recommended Approach

**Use FastAPI + MCP SDK** for maximum flexibility:

1. Create FastAPI application
2. Implement `/mcp` endpoint
3. Handle JSON-RPC message routing
4. Reuse existing tool implementations
5. Add SSE support for streaming
6. Package in Docker container
7. Deploy to Scaleway Serverless Containers

## Deployment Steps

1. **Adapt Server Code**
   - Convert from STDIO to HTTP transport
   - Add FastAPI application
   - Implement MCP HTTP protocol
   - Keep existing tool functions

2. **Create Dockerfile**
   - Use Python 3.11 base image
   - Install dependencies (FastAPI, uvicorn, scaleway, mcp)
   - Copy server code
   - Expose port (default 8080)
   - Set entrypoint to run FastAPI server

3. **Build and Push Image**
   - Build Docker image
   - Tag image appropriately
   - Push to Scaleway Container Registry or Docker Hub

4. **Deploy to Scaleway**
   - Create Serverless Container namespace
   - Deploy container with environment variables
   - Configure auto-scaling
   - Set up health checks

5. **Test Deployment**
   - Verify HTTP endpoint accessibility
   - Test MCP protocol compliance
   - Validate tool execution
   - Check auto-scaling behavior

## Environment Variables for Deployment

```
SCW_ACCESS_KEY=<access_key>
SCW_SECRET_KEY=<secret_key>
SCW_PROJECT_ID=<project_id>
SCW_ORGANIZATION_ID=<organization_id>
SCW_DEFAULT_REGION=fr-par
SCW_DEFAULT_ZONE=fr-par-1
PORT=8080  # Scaleway will inject this
```

## Security Considerations

1. **Origin Validation**: Validate Origin header to prevent DNS rebinding
2. **Authentication**: Implement proper auth for HTTP endpoints
3. **Secrets Management**: Use Scaleway secrets for sensitive data
4. **HTTPS Only**: Ensure all traffic is encrypted
5. **Rate Limiting**: Implement rate limiting to prevent abuse
