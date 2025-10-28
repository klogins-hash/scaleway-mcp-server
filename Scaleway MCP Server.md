# Scaleway MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that enables AI assistants like [Manus](https://manus.im) to interact with [Scaleway](https://www.scaleway.com) cloud infrastructure programmatically.

## Features

This MCP server provides tools for managing Scaleway resources:

### Instance Management
- `list_instances` - List all compute instances in a zone
- `get_instance` - Get detailed information about a specific instance
- `create_instance` - Create a new compute instance
- `start_instance` - Start a stopped instance
- `stop_instance` - Stop a running instance
- `delete_instance` - Delete an instance

### Network Management
- `list_private_networks` - List all private networks in a region
- `create_private_network` - Create a new private network

### Kubernetes Management
- `list_k8s_clusters` - List all Kubernetes clusters in a region
- `get_k8s_cluster` - Get detailed information about a Kubernetes cluster

### Image Management
- `list_images` - List available instance images

## Prerequisites

- Python 3.1your_access_key_here or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Scaleway account with API credentials

## Installation

### 1. Install uv (if not already installed)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone or download this repository

```bash
git clone <repository-url>
cd scaleway-mcp-server
```

### 3. Install dependencies

```bash
uv sync
```

## Configuration

### Get Scaleway API Credentials

1. Log in to [Scaleway Console](https://console.scaleway.com)
2. Navigate to **IAM** → **API Keys**
3. Create a new API key or use an existing one
4. Note down:
   - Access Key (e.g., `SCW7JHKD4NQXX6YWY5A4`)
   - Secret Key (e.g., `eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34`)
   - Default Project ID
   - Organization ID

### Environment Variables

The server requires the following environment variables:

```bash
SCW_ACCESS_KEY=<your-access-key>
SCW_SECRET_KEY=<your-secret-key>
SCW_PROJECT_ID=<your-project-id>
SCW_ORGANIZATION_ID=<your-organization-id>
SCW_DEFAULT_REGION=fr-par  # Optional, defaults to fr-par
SCW_DEFAULT_ZONE=fr-par-1  # Optional, defaults to fr-par-1
```

You can copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Usage

### Running the Server Standalone

For testing purposes, you can run the server directly:

```bash
# Set environment variables
export SCW_ACCESS_KEY=SCW7JHKD4NQXX6YWY5A4
export SCW_SECRET_KEY=eayour_access_key_here79fb9-3edf-4391-a785-d29cyour_access_key_here3c7bd34
export SCW_PROJECT_ID=b6c2c4f2-4697-4927-958your_access_key_here-143bf8c3f588
export SCW_ORGANIZATION_ID=c5d299b8-8462-4your_access_key_herefb-b5ae-32a88your_access_key_here8bf394

# Run the server
uv run scaleway_server.py
```

### Integration with Manus

To use this MCP server with Manus, you need to configure it in your Manus MCP settings.

#### Step 1: Locate your Manus MCP configuration

The configuration location depends on your operating system:

- **macOS**: `~/Library/Application Support/manus/mcp.json`
- **Linux**: `~/.config/manus/mcp.json`
- **Windows**: `%APPDATA%\manus\mcp.json`

#### Step 2: Add the Scaleway server configuration

Add the following to your `mcp.json` file:

```json
{
  "mcpServers": {
    "scaleway": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/scaleway-mcp-server",
        "scaleway_server.py"
      ],
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

**Important**: Replace `/absolute/path/to/scaleway-mcp-server` with the actual absolute path to this directory.

#### Step 3: Restart Manus

After updating the configuration, restart Manus to load the new MCP server.

#### Step 4: Use the connector

Once configured, you can interact with Scaleway through Manus using natural language:

**Example prompts:**
- "List all my Scaleway instances"
- "Create a new instance named 'web-server' with type DEV1-S"
- "Show me details of instance xyz123"
- "Stop instance xyz123"
- "List all my Kubernetes clusters"
- "Show me available images in fr-par-1 zone"

### Testing with MCP Inspector

You can test the server using the MCP Inspector tool:

```bash
npx @modelcontextprotocol/inspector uv run scaleway_server.py
```

This will open a web interface where you can test individual tools.

## Available Tools

### Instance Management

#### `list_instances`
List all compute instances in a zone.

**Parameters:**
- `zone` (optional): Scaleway zone (e.g., `fr-par-1`, `nl-ams-1`)

**Example:**
```
List all instances in fr-par-1 zone
```

#### `get_instance`
Get detailed information about a specific instance.

**Parameters:**
- `instance_id` (required): The ID of the instance
- `zone` (optional): Scaleway zone

**Example:**
```
Show me details of instance 11111111-1111-1111-1111-111111111111
```

#### `create_instance`
Create a new compute instance.

**Parameters:**
- `name` (required): Name for the new instance
- `instance_type` (required): Instance type (e.g., `DEV1-S`, `GP1-XS`, `PLAY2-NANO`)
- `image_id` (required): Image ID to use
- `zone` (optional): Scaleway zone
- `tags` (optional): List of tags

**Example:**
```
Create a new instance named 'my-server' with type DEV1-S using image xyz
```

#### `start_instance`
Start a stopped instance.

**Parameters:**
- `instance_id` (required): The ID of the instance to start
- `zone` (optional): Scaleway zone

#### `stop_instance`
Stop a running instance.

**Parameters:**
- `instance_id` (required): The ID of the instance to stop
- `zone` (optional): Scaleway zone

#### `delete_instance`
Delete an instance.

**Parameters:**
- `instance_id` (required): The ID of the instance to delete
- `zone` (optional): Scaleway zone

### Network Management

#### `list_private_networks`
List all private networks in a region.

**Parameters:**
- `region` (optional): Scaleway region (e.g., `fr-par`, `nl-ams`)

#### `create_private_network`
Create a new private network.

**Parameters:**
- `name` (required): Name for the new private network
- `region` (optional): Scaleway region
- `tags` (optional): List of tags

### Kubernetes Management

#### `list_k8s_clusters`
List all Kubernetes clusters in a region.

**Parameters:**
- `region` (optional): Scaleway region

#### `get_k8s_cluster`
Get detailed information about a Kubernetes cluster.

**Parameters:**
- `cluster_id` (required): The ID of the cluster
- `region` (optional): Scaleway region

### Image Management

#### `list_images`
List available instance images.

**Parameters:**
- `zone` (optional): Scaleway zone
- `arch` (optional): Filter by architecture (`x86_64` or `arm64`)

## Scaleway Regions and Zones

### Available Regions
- `fr-par` - Paris, France
- `nl-ams` - Amsterdam, Netherlands
- `pl-waw` - Warsaw, Poland

### Available Zones
- `fr-par-1`, `fr-par-2`, `fr-par-3` - Paris zones
- `nl-ams-1`, `nl-ams-2`, `nl-ams-3` - Amsterdam zones
- `pl-waw-1`, `pl-waw-2`, `pl-waw-3` - Warsaw zones

## Common Instance Types

### Development
- `DEV1-S` - 2 vCPUs, 2GB RAM
- `DEV1-M` - 3 vCPUs, 4GB RAM
- `DEV1-L` - 4 vCPUs, 8GB RAM
- `DEV1-XL` - 4 vCPUs, 12GB RAM

### General Purpose
- `GP1-XS` - 4 vCPUs, 16GB RAM
- `GP1-S` - 8 vCPUs, 32GB RAM
- `GP1-M` - 16 vCPUs, 64GB RAM
- `GP1-L` - 32 vCPUs, 128GB RAM

### Play (Cost-Optimized)
- `PLAY2-PICO` - 1 vCPU, 2GB RAM
- `PLAY2-NANO` - 2 vCPUs, 4GB RAM
- `PLAY2-MICRO` - 4 vCPUs, 8GB RAM

For a complete list, visit the [Scaleway pricing page](https://www.scaleway.com/en/pricing/).

## Troubleshooting

### Server won't start

**Issue**: Error about missing credentials

**Solution**: Ensure all required environment variables are set:
```bash
echo $SCW_ACCESS_KEY
echo $SCW_SECRET_KEY
echo $SCW_PROJECT_ID
```

### Manus doesn't recognize the server

**Issue**: Server not showing up in Manus

**Solutions**:
1. Check that the path in `mcp.json` is absolute, not relative
2. Verify that `uv` is installed and in your PATH
3. Check Manus logs for error messages
4. Restart Manus after configuration changes

### API errors

**Issue**: "Unauthorized" or "Invalid credentials"

**Solutions**:
1. Verify your API credentials in the Scaleway Console
2. Ensure the API key has the necessary permissions
3. Check that the project ID and organization ID are correct

### Permission errors

**Issue**: "Permission denied" when creating resources

**Solution**: Ensure your API key has the appropriate IAM permissions for the operations you're trying to perform.

## Security Best Practices

1. **Never commit credentials**: Don't commit `.env` files or hardcode credentials
2. **Use environment variables**: Always load credentials from environment variables
3. **Limit API key permissions**: Create API keys with only the permissions you need
4. **Rotate keys regularly**: Periodically rotate your API keys
5. **Use separate keys**: Use different API keys for development and production

## Development

### Project Structure

```
scaleway-mcp-server/
├── scaleway_server.py    # Main server implementation
├── pyproject.toml         # Python project configuration
├── .env.example           # Example environment variables
└── README.md              # This file
```

### Adding New Tools

To add a new tool:

1. Define the tool function with the `@mcp.tool()` decorator
2. Add proper type hints and docstring
3. Implement error handling
4. Test with MCP Inspector

Example:

```python
@mcp.tool()
async def my_new_tool(param: str) -> str:
    """Description of what the tool does.
    
    Args:
        param: Description of the parameter
    """
    try:
        client = get_scaleway_client()
        # Implementation here
        return "Success message"
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"Error: {str(e)}"
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is provided as-is for use with Scaleway and Manus.im.

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Scaleway API Documentation](https://www.scaleway.com/en/developers/api/)
- [Scaleway Python SDK](https://github.com/scaleway/scaleway-sdk-python)
- [Manus.im](https://manus.im)

## Support

For issues related to:
- **This MCP server**: Open an issue in this repository
- **Scaleway API**: Visit [Scaleway Support](https://console.scaleway.com/support)
- **Manus**: Visit [Manus Help](https://help.manus.im)
- **MCP Protocol**: Visit [MCP Community](https://github.com/modelcontextprotocol)
