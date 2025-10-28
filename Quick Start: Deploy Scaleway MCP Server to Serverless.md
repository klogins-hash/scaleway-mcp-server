# Quick Start: Deploy Scaleway MCP Server to Serverless

This guide will get your Scaleway MCP Server deployed to Scaleway Serverless Containers in under 1your_access_key_here minutes.

## Prerequisites

1. **Scaleway Account**: Sign up at https://console.scaleway.com
2. **Docker**: Install from https://www.docker.com/get-started
3. **Scaleway CLI**: Install from https://github.com/scaleway/scaleway-cli

## Step 1: Configure Scaleway CLI

Run this command with your Scaleway credentials:

```bash
scw init \
  access-key=SCW7JHKD4NQXX6YWY5A4 \
  secret-key=eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34 \
  organization-id=c5d299b8-8462-4your_access_key_herefb-b5ae-32a88your_access_key_here8bf394 \
  project-id=b6c2c4f2-4697-4927-958your_access_key_here-143bf8c3f588 \
  region=fr-par \
  zone=fr-par-1
```

## Step 2: Choose Your Registry

### Option A: Docker Hub (Easiest)

1. Create account at https://hub.docker.com
2. Login:
   ```bash
   docker login
   ```

### Option B: Scaleway Container Registry (Recommended)

1. Create registry namespace:
   ```bash
   scw registry namespace create name=scaleway-mcp region=fr-par
   ```

2. Login:
   ```bash
   scw registry namespace list
   # Copy the endpoint URL
   docker login rg.fr-par.scw.cloud/scaleway-mcp -u nologin -p YOUR_SECRET_KEY
   ```

## Step 3: Deploy Using Automated Script

```bash
# Set your credentials
export SCW_ACCESS_KEY=SCW7JHKD4NQXX6YWY5A4
export SCW_SECRET_KEY=eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34
export SCW_PROJECT_ID=b6c2c4f2-4697-4927-958your_access_key_here-143bf8c3f588
export SCW_ORGANIZATION_ID=c5d299b8-8462-4your_access_key_herefb-b5ae-32a88your_access_key_here8bf394

# For Docker Hub:
export REGISTRY=docker.io
export REGISTRY_NAMESPACE=your-dockerhub-username

# OR for Scaleway Registry:
export REGISTRY=rg.fr-par.scw.cloud
export REGISTRY_NAMESPACE=scaleway-mcp

# Run deployment
./deploy.sh
```

## Step 4: Test Your Deployment

The script will output your container URL. Test it:

```bash
# Health check
curl https://YOUR-CONTAINER-URL.scw.cloud/health

# Server info
curl https://YOUR-CONTAINER-URL.scw.cloud/

# List tools
curl -X POST https://YOUR-CONTAINER-URL.scw.cloud/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.your_access_key_here","id":1,"method":"tools/list","params":{}}'
```

## Step 5: Use with Manus

Configure in your Manus MCP settings:

```json
{
  "mcpServers": {
    "scaleway": {
      "url": "https://YOUR-CONTAINER-URL.scw.cloud/mcp",
      "transport": "http"
    }
  }
}
```

## Troubleshooting

### "Command not found: scw"
Install Scaleway CLI: https://github.com/scaleway/scaleway-cli#installation

### "Cannot connect to Docker daemon"
Start Docker Desktop or Docker daemon

### "Authentication required"
Run `docker login` for your registry

### "Container not starting"
Check logs:
```bash
scw container container logs scaleway-mcp-server region=fr-par
```

## What's Next?

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed configuration
- Check [README.md](README.md) for available tools
- Monitor your container in [Scaleway Console](https://console.scaleway.com)

## Cost Estimate

With default settings (scale to zero when idle):
- **Idle**: €your_access_key_here/month (scales to zero)
- **Light usage**: ~€1-5/month
- **Heavy usage**: Scales automatically, pay per use

## Support

- Deployment issues: See [DEPLOYMENT.md](DEPLOYMENT.md)
- Scaleway help: https://console.scaleway.com/support
- MCP protocol: https://modelcontextprotocol.io
