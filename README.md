# Scaleway MCP Server

A comprehensive Model Context Protocol (MCP) server for managing Scaleway cloud infrastructure. This server provides both local STDIO and HTTP-based interfaces for seamless integration with MCP clients.

## 🚀 Features

- **Complete Scaleway API Coverage**: Manage instances, databases, storage, networking, and more
- **Dual Deployment Options**: Local STDIO server and HTTP server for remote access
- **Serverless Ready**: Deploy to Scaleway Serverless Containers with one command
- **MCP Protocol Compliant**: Full support for MCP 2024-11-05 specification
- **Production Ready**: Docker containerization, health checks, and monitoring

## 🛠️ Available Tools

### Instance Management
- `list_instances` - List all compute instances
- `get_instance` - Get detailed instance information  
- `start_instance` - Start stopped instances
- `stop_instance` - Stop running instances

### Kubernetes
- `list_k8s_clusters` - List all Kubernetes clusters

### Database Management
- `list_databases` - List PostgreSQL, MySQL databases
- `get_database` - Get detailed database information

### Object Storage
- `list_buckets` - List all S3-compatible storage buckets

### Container Registry
- `list_registries` - List container registries and images

### Load Balancers
- `list_load_balancers` - List all load balancers

### Serverless
- `list_functions` - List all serverless functions
- `list_containers` - List all serverless containers

### Redis & Networking
- `list_redis_clusters` - List Redis clusters
- `list_private_networks` - List VPCs and private networks

### Marketplace
- `list_marketplace_images` - Browse available OS/app images

## 📦 Quick Start

### 1. Local Development

```bash
# Clone the repository
git clone <repository-url>
cd scaleway-mcp-server

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your Scaleway credentials

# Run the STDIO server
uv run scaleway_server.py

# Or run the HTTP server
uv run scaleway_http_server.py
```

### 2. Serverless Deployment

```bash
# Configure Scaleway CLI
scw init

# Deploy to Scaleway Serverless Containers
./deploy.sh
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SCW_ACCESS_KEY` | Scaleway access key | `your_access_key_here` |
| `SCW_SECRET_KEY` | Scaleway secret key | `your_secret_key_here` |
| `SCW_PROJECT_ID` | Scaleway project ID | `your_project_id_here` |
| `SCW_ORGANIZATION_ID` | Scaleway organization ID | `your_organization_id_here` |
| `SCW_DEFAULT_REGION` | Default region | `fr-par` |
| `SCW_DEFAULT_ZONE` | Default zone | `fr-par-1` |

### MCP Client Configuration

For HTTP transport:
```json
{
  "mcpServers": {
    "scaleway": {
      "transport": "http",
      "url": "https://your-deployment-url/mcp"
    }
  }
}
```

For STDIO transport:
```json
{
  "mcpServers": {
    "scaleway": {
      "command": "uv",
      "args": ["run", "scaleway_server.py"],
      "cwd": "/path/to/scaleway-mcp-server"
    }
  }
}
```

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t scaleway-mcp-server .

# Run locally
docker run -p 8080:8080 \
  -e SCW_ACCESS_KEY=your_access_key_here \
  -e SCW_SECRET_KEY=your_secret_key_here \
  -e SCW_PROJECT_ID=your_project_id_here \
  -e SCW_ORGANIZATION_ID=your_organization_id_here \
  scaleway-mcp-server
```

## 📚 Documentation

- [Complete Setup Guide](Scaleway%20MCP%20Server.md)
- [Serverless Deployment Guide](Scaleway%20MCP%20Server%20-%20Serverless%20Deployment%20Guide.md)
- [Quick Start Guide](Quick%20Start%3A%20Deploy%20Scaleway%20MCP%20Server%20to%20Serverless.md)
- [Architecture Design](architecture_design.md)

## 🔐 Security

- Never commit real credentials to version control
- Use environment variables or secure secret management
- The server validates API credentials on startup
- All API calls use official Scaleway SDK with proper authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Check the [documentation](docs/) for detailed guides
- Open an issue for bugs or feature requests
- Review the [architecture design](architecture_design.md) for technical details

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │    │  Scaleway MCP    │    │  Scaleway API   │
│   (Manus, etc)  │◄──►│     Server       │◄──►│   (Official)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Scaleway Cloud  │
                       │   Infrastructure │
                       └──────────────────┘
```

The server acts as a bridge between MCP clients and the Scaleway cloud platform, providing a standardized interface for infrastructure management.
