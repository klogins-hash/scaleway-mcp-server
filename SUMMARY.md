# Scaleway MCP Server - Serverless Deployment Package

## What's Included

This package contains everything needed to deploy the Scaleway MCP Server as a serverless container on Scaleway.

### Core Files

#### 1. Server Implementations

**`scaleway_server.py`** - STDIO-based MCP server
- For local use with Manus desktop app
- Uses standard input/output for communication
- Launched as subprocess by MCP client

**`scaleway_http_server.py`** - HTTP-based MCP server
- For serverless deployment
- Exposes HTTP endpoints for remote access
- Built with FastAPI for production use

#### 2. Deployment Files

**`Dockerfile`** - Container image definition
- Based on Python 3.11 slim
- Installs dependencies with uv
- Configured for Scaleway Serverless Containers
- Includes health checks

**`deploy.sh`** - Automated deployment script
- Builds Docker image
- Pushes to container registry
- Deploys to Scaleway Serverless Containers
- Configures environment variables

**`.dockerignore`** - Docker build exclusions
- Excludes unnecessary files from image
- Reduces image size
- Improves build performance

#### 3. Configuration Files

**`pyproject.toml`** - Python project configuration
- Managed by uv
- Lists all dependencies
- Project metadata

**`uv.lock`** - Dependency lock file
- Ensures reproducible builds
- Pins exact versions

**`.env.example`** - Environment variables template
- Example credentials
- Configuration options

**`mcp-config-example.json`** - Manus configuration example
- For local STDIO deployment
- Shows how to configure in Manus

#### 4. Documentation

**`README.md`** - Main documentation
- Installation instructions
- Usage guide
- Available tools
- Troubleshooting

**`DEPLOYMENT.md`** - Serverless deployment guide
- Detailed deployment instructions
- Configuration options
- Testing procedures
- Production checklist

**`QUICKSTART.md`** - Quick start guide
- 10-minute deployment guide
- Step-by-step instructions
- Common issues and solutions

**`SUMMARY.md`** - This file
- Package overview
- File descriptions

#### 5. Testing

**`test_server.py`** - Server validation script
- Tests imports
- Validates server initialization
- Checks Scaleway client setup

### Project Structure

```
scaleway-mcp-server/
├── scaleway_server.py          # STDIO MCP server
├── scaleway_http_server.py     # HTTP MCP server
├── Dockerfile                   # Container definition
├── deploy.sh                    # Deployment script
├── .dockerignore                # Docker exclusions
├── .gitignore                   # Git exclusions
├── pyproject.toml               # Project config
├── uv.lock                      # Dependency lock
├── .env.example                 # Env vars template
├── mcp-config-example.json      # Manus config
├── test_server.py               # Test script
├── README.md                    # Main docs
├── DEPLOYMENT.md                # Deployment guide
├── QUICKSTART.md                # Quick start
└── SUMMARY.md                   # This file
```

## Available Tools

The MCP server provides these tools for managing Scaleway infrastructure:

### Instance Management
1. **list_instances** - List all compute instances
2. **get_instance** - Get instance details
3. **create_instance** - Create new instance
4. **start_instance** - Start stopped instance
5. **stop_instance** - Stop running instance
6. **delete_instance** - Delete instance

### Network Management
7. **list_private_networks** - List private networks
8. **create_private_network** - Create private network

### Kubernetes Management
9. **list_k8s_clusters** - List Kubernetes clusters
10. **get_k8s_cluster** - Get cluster details

### Image Management
11. **list_images** - List available images

## Deployment Options

### Option 1: Local STDIO (Desktop)

Use `scaleway_server.py` with Manus desktop app:

```json
{
  "mcpServers": {
    "scaleway": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/scaleway-mcp-server", "scaleway_server.py"],
      "env": {
        "SCW_ACCESS_KEY": "...",
        "SCW_SECRET_KEY": "...",
        "SCW_PROJECT_ID": "..."
      }
    }
  }
}
```

### Option 2: Serverless HTTP (Cloud)

Deploy `scaleway_http_server.py` to Scaleway Serverless Containers:

```bash
./deploy.sh
```

Access via HTTPS endpoint:
```
https://your-container.scw.cloud/mcp
```

## Key Features

### STDIO Server
- ✅ Works with Manus desktop
- ✅ No network latency
- ✅ Secure local execution
- ❌ Cannot be accessed remotely
- ❌ Requires local installation

### HTTP Server
- ✅ Remote access via HTTPS
- ✅ Auto-scaling
- ✅ High availability
- ✅ Pay-per-use pricing
- ❌ Network latency
- ❌ Requires deployment

## Getting Started

### For Local Use

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set environment variables:
   ```bash
   export SCW_ACCESS_KEY=...
   export SCW_SECRET_KEY=...
   export SCW_PROJECT_ID=...
   ```

3. Configure in Manus (see README.md)

### For Serverless Deployment

1. Follow QUICKSTART.md
2. Run `./deploy.sh`
3. Test deployment
4. Configure remote access

## Requirements

### Local Deployment
- Python 3.10+
- uv package manager
- Scaleway API credentials

### Serverless Deployment
- Docker
- Scaleway CLI
- Container registry access
- Scaleway account

## Support Resources

- **Installation**: See README.md
- **Deployment**: See DEPLOYMENT.md or QUICKSTART.md
- **Troubleshooting**: Check documentation
- **Scaleway Help**: https://console.scaleway.com/support
- **MCP Protocol**: https://modelcontextprotocol.io

## Version Information

- **Server Version**: 1.0.0
- **MCP Protocol**: 2024-11-05
- **Python**: 3.11+
- **FastAPI**: 0.120.1
- **Scaleway SDK**: 2.10.2

## License

This project is provided as-is for use with Scaleway and Manus.im.

## Next Steps

1. **Read** QUICKSTART.md for fastest deployment
2. **Or** read DEPLOYMENT.md for detailed guide
3. **Configure** your Scaleway credentials
4. **Deploy** using automated script
5. **Test** your deployment
6. **Integrate** with Manus or other MCP clients

## Questions?

Check the documentation files included in this package:
- README.md - General usage
- DEPLOYMENT.md - Serverless deployment
- QUICKSTART.md - Fast deployment guide
