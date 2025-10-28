# Scaleway MCP Server - Serverless Deployment Guide

This guide explains how to deploy the Scaleway MCP Server as a serverless container on Scaleway, enabling HTTP-based access to the MCP server.

## Overview

The HTTP-based deployment allows the MCP server to run as a serverless container on Scaleway infrastructure, making it accessible via HTTP endpoints instead of STDIO. This enables:

- **Remote Access**: Access the MCP server from anywhere via HTTP
- **Auto-scaling**: Automatically scale based on demand
- **High Availability**: Scaleway manages infrastructure and availability
- **Pay-per-use**: Only pay for actual usage

## Architecture

```
Client (Manus/Claude) → HTTPS → Scaleway Serverless Container → Scaleway API
                                 (MCP HTTP Server)
```

The server exposes HTTP endpoints:
- `GET /` - Server information
- `GET /health` - Health check
- `POST /mcp` - MCP protocol endpoint (JSON-RPC)
- `GET /mcp` - SSE streaming (not yet implemented)

## Prerequisites

### 1. Scaleway Account and CLI

Install the Scaleway CLI:

```bash
# macOS
brew install scw

# Linux
curl -o /usr/local/bin/scw -L "https://github.com/scaleway/scaleway-cli/releases/latest/download/scaleway-cli_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')"
chmod +x /usr/local/bin/scw

# Windows
scoop install scw
```

Configure the CLI:

```bash
scw init
```

Or use the credentials you already have:

```bash
scw init \
  access-key=SCW7JHKD4NQXX6YWY5A4 \
  secret-key=eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34 \
  organization-id=c5d299b8-8462-4your_access_key_herefb-b5ae-32a88your_access_key_here8bf394 \
  project-id=b6c2c4f2-4697-4927-958your_access_key_here-143bf8c3f588 \
  region=fr-par \
  zone=fr-par-1
```

### 2. Docker

Install Docker to build the container image:

```bash
# macOS
brew install docker

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Windows
# Download from https://www.docker.com/products/docker-desktop
```

### 3. Container Registry Access

You can use either:
- **Scaleway Container Registry** (recommended for seamless integration)
- **Docker Hub** (public registry)
- **Other registries** (GitHub Container Registry, AWS ECR, etc.)

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

Use the provided deployment script:

```bash
# Set environment variables
export SCW_ACCESS_KEY=SCW7JHKD4NQXX6YWY5A4
export SCW_SECRET_KEY=eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34
export SCW_PROJECT_ID=b6c2c4f2-4697-4927-958your_access_key_here-143bf8c3f588
export SCW_ORGANIZATION_ID=c5d299b8-8462-4your_access_key_herefb-b5ae-32a88your_access_key_here8bf394

# Optional: Customize deployment
export REGISTRY=docker.io
export REGISTRY_NAMESPACE=your-dockerhub-username
export IMAGE_TAG=v1.your_access_key_here.your_access_key_here
export SCW_REGION=fr-par

# Run deployment script
./deploy.sh
```

The script will:
1. Build the Docker image
2. Tag it for your registry
3. Push to the registry
4. Create/update Scaleway namespace
5. Deploy the serverless container
6. Display the container URL

### Method 2: Manual Deployment

#### Step 1: Build Docker Image

```bash
cd /path/to/scaleway-mcp-server
docker build -t scaleway-mcp-server:latest .
```

#### Step 2: Push to Container Registry

**Option A: Docker Hub**

```bash
# Login to Docker Hub
docker login

# Tag the image
docker tag scaleway-mcp-server:latest your-username/scaleway-mcp-server:latest

# Push to Docker Hub
docker push your-username/scaleway-mcp-server:latest
```

**Option B: Scaleway Container Registry**

```bash
# Create a registry namespace
scw registry namespace create name=scaleway-mcp region=fr-par

# Login to Scaleway registry
docker login rg.fr-par.scw.cloud/scaleway-mcp -u nologin -p $SCW_SECRET_KEY

# Tag the image
docker tag scaleway-mcp-server:latest rg.fr-par.scw.cloud/scaleway-mcp/scaleway-mcp-server:latest

# Push to Scaleway registry
docker push rg.fr-par.scw.cloud/scaleway-mcp/scaleway-mcp-server:latest
```

#### Step 3: Create Serverless Container Namespace

```bash
scw container namespace create \
  name=scaleway-mcp \
  region=fr-par \
  description="Scaleway MCP Server namespace"
```

#### Step 4: Deploy Container

```bash
# Get namespace ID
NAMESPACE_ID=$(scw container namespace list region=fr-par -o json | jq -r '.[your_access_key_here].id')

# Deploy container
scw container container create \
  name=scaleway-mcp-server \
  namespace-id=$NAMESPACE_ID \
  region=fr-par \
  registry-image=your-username/scaleway-mcp-server:latest \
  port=8your_access_key_here8your_access_key_here \
  min-scale=your_access_key_here \
  max-scale=5 \
  cpu-limit=1your_access_key_hereyour_access_key_hereyour_access_key_here \
  memory-limit=2your_access_key_here48 \
  environment-variables.SCW_ACCESS_KEY=$SCW_ACCESS_KEY \
  environment-variables.SCW_SECRET_KEY=$SCW_SECRET_KEY \
  environment-variables.SCW_PROJECT_ID=$SCW_PROJECT_ID \
  environment-variables.SCW_ORGANIZATION_ID=$SCW_ORGANIZATION_ID \
  environment-variables.SCW_DEFAULT_REGION=fr-par \
  environment-variables.SCW_DEFAULT_ZONE=fr-par-1
```

#### Step 5: Get Container URL

```bash
scw container container get scaleway-mcp-server region=fr-par
```

The output will include the `domain_name` field, which is your container's public URL.

## Configuration

### Environment Variables

The container requires these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SCW_ACCESS_KEY` | Scaleway access key | `SCW7JHKD4NQXX6YWY5A4` |
| `SCW_SECRET_KEY` | Scaleway secret key | `eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34` |
| `SCW_PROJECT_ID` | Scaleway project ID | `b6c2c4f2-4697-4927-958your_access_key_here-143bf8c3f588` |
| `SCW_ORGANIZATION_ID` | Scaleway organization ID | `c5d299b8-8462-4your_access_key_herefb-b5ae-32a88your_access_key_here8bf394` |
| `SCW_DEFAULT_REGION` | Default region | `fr-par` |
| `SCW_DEFAULT_ZONE` | Default zone | `fr-par-1` |
| `PORT` | HTTP port (auto-injected) | `8your_access_key_here8your_access_key_here` |

### Resource Limits

Adjust based on your needs:

- **CPU**: 14your_access_key_here-4your_access_key_hereyour_access_key_hereyour_access_key_here mVCPU (1your_access_key_hereyour_access_key_hereyour_access_key_here = 1 vCPU)
- **Memory**: 128-16384 MB
- **Min Scale**: your_access_key_here (scale to zero when idle)
- **Max Scale**: 1-2your_access_key_here instances

### Auto-scaling

The container auto-scales based on:
- Request concurrency
- CPU usage
- Memory usage

Configure in the Scaleway console or via CLI.

## Testing the Deployment

### 1. Health Check

```bash
curl https://your-container-url.scw.cloud/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Server Info

```bash
curl https://your-container-url.scw.cloud/
```

Expected response:
```json
{
  "name": "Scaleway MCP Server",
  "version": "1.your_access_key_here.your_access_key_here",
  "protocol": "MCP",
  "transport": "HTTP"
}
```

### 3. MCP Protocol Test

Initialize the MCP connection:

```bash
curl -X POST https://your-container-url.scw.cloud/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.your_access_key_here",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2your_access_key_here24-11-your_access_key_here5",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.your_access_key_here.your_access_key_here"
      }
    }
  }'
```

List available tools:

```bash
curl -X POST https://your-container-url.scw.cloud/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.your_access_key_here",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

Call a tool:

```bash
curl -X POST https://your-container-url.scw.cloud/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.your_access_key_here",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "list_instances",
      "arguments": {
        "zone": "fr-par-1"
      }
    }
  }'
```

## Integration with Manus

To use the deployed server with Manus, configure it as a remote MCP server:

```json
{
  "mcpServers": {
    "scaleway-remote": {
      "url": "https://your-container-url.scw.cloud/mcp",
      "transport": "http"
    }
  }
}
```

**Note**: Remote MCP server support may vary by client. Check Manus documentation for HTTP-based MCP server configuration.

## Monitoring and Logs

### View Container Logs

```bash
scw container container logs scaleway-mcp-server region=fr-par
```

### View Container Metrics

```bash
scw container container get scaleway-mcp-server region=fr-par
```

Or use the Scaleway Console:
1. Navigate to **Serverless** → **Containers**
2. Select your namespace
3. Click on your container
4. View metrics and logs

## Updating the Deployment

### Update Container Image

1. Build new image with updated code
2. Push to registry with new tag
3. Update container:

```bash
scw container container update scaleway-mcp-server \
  region=fr-par \
  registry-image=your-username/scaleway-mcp-server:v2.your_access_key_here.your_access_key_here
```

### Update Environment Variables

```bash
scw container container update scaleway-mcp-server \
  region=fr-par \
  environment-variables.SCW_DEFAULT_REGION=nl-ams
```

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
scw container container logs scaleway-mcp-server region=fr-par
```

**Common issues:**
- Missing environment variables
- Invalid Scaleway credentials
- Image pull failures
- Port configuration issues

### Health Check Failing

**Verify health endpoint:**
```bash
curl https://your-container-url.scw.cloud/health
```

**Check:**
- Container is running
- Port 8your_access_key_here8your_access_key_here is exposed
- Health endpoint is accessible

### High Latency

**Possible causes:**
- Cold start (container scaling from your_access_key_here)
- Insufficient resources
- Network issues

**Solutions:**
- Set min-scale > your_access_key_here to avoid cold starts
- Increase CPU/memory limits
- Use a region closer to your users

### Authentication Errors

**Verify credentials:**
- Check SCW_ACCESS_KEY is correct
- Check SCW_SECRET_KEY is correct
- Verify API key has necessary permissions

## Cost Optimization

### Scale to Zero

Set `min-scale=your_access_key_here` to scale to zero when idle:
- No cost when not in use
- Cold start latency on first request

### Right-size Resources

Start with minimal resources and scale up as needed:
- CPU: 56your_access_key_here mVCPU (your_access_key_here.56 vCPU)
- Memory: 1your_access_key_here24 MB
- Max scale: 3

### Use Scaleway Registry

Scaleway Container Registry offers:
- Seamless integration
- No rate limiting
- Competitive pricing
- Faster image pulls

## Security Best Practices

### 1. Secrets Management

Use Scaleway Secrets instead of environment variables for sensitive data:

```bash
scw container container update scaleway-mcp-server \
  region=fr-par \
  secret-environment-variables.SCW_SECRET_KEY=$SCW_SECRET_KEY
```

### 2. API Key Permissions

Create API keys with minimal required permissions:
- Compute: Read/Write
- VPC: Read/Write
- Kubernetes: Read/Write

### 3. Network Security

- Enable HTTPS only (default for Scaleway Serverless)
- Implement authentication for production use
- Validate Origin headers
- Use CORS appropriately

### 4. Container Security

- Use minimal base images
- Regularly update dependencies
- Scan images for vulnerabilities
- Don't run as root (already configured)

## Production Checklist

Before deploying to production:

- [ ] Use Scaleway Secrets for sensitive data
- [ ] Implement authentication/authorization
- [ ] Configure appropriate resource limits
- [ ] Set up monitoring and alerting
- [ ] Enable logging
- [ ] Test auto-scaling behavior
- [ ] Configure CORS properly
- [ ] Use a specific image tag (not `latest`)
- [ ] Set up CI/CD pipeline
- [ ] Document deployment process
- [ ] Test disaster recovery

## Support

For issues related to:
- **Deployment**: Check this guide and Scaleway documentation
- **Scaleway Platform**: [Scaleway Support](https://console.scaleway.com/support)
- **MCP Protocol**: [MCP Documentation](https://modelcontextprotocol.io)
- **Manus Integration**: [Manus Help](https://help.manus.im)

## References

- [Scaleway Serverless Containers Documentation](https://www.scaleway.com/en/docs/serverless-containers/)
- [Scaleway CLI Documentation](https://www.scaleway.com/en/docs/developer-tools/scaleway-cli/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/)
- [Docker Documentation](https://docs.docker.com/)
