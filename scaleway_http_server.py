#!/usr/bin/env python3
"""
Scaleway MCP Server - HTTP Version (Simple)
A Model Context Protocol server for managing Scaleway infrastructure via HTTP.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from mcp.server import Server
from mcp.server.models import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)
from mcp import types

from scaleway import Client
from scaleway.instance.v1.api import InstanceV1API
from scaleway.k8s.v1.api import K8SV1API

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("scaleway-mcp-http")

# Global Scaleway client
scaleway_client: Optional[Client] = None
mcp_server: Optional[Server] = None


def get_scaleway_client() -> Client:
    """Get or create Scaleway client with credentials from environment variables."""
    global scaleway_client
    
    if scaleway_client is not None:
        return scaleway_client
    
    access_key = os.getenv("SCW_ACCESS_KEY") or os.getenv("SCALEWAY_ACCESS_KEY")
    secret_key = os.getenv("SCW_SECRET_KEY") or os.getenv("SCALEWAY_SECRET_KEY")
    project_id = os.getenv("SCW_PROJECT_ID") or os.getenv("SCALEWAY_PROJECT_ID")
    organization_id = os.getenv("SCW_ORGANIZATION_ID") or os.getenv("SCALEWAY_ORGANIZATION_ID")
    default_region = os.getenv("SCW_DEFAULT_REGION") or os.getenv("SCALEWAY_DEFAULT_REGION", "fr-par")
    default_zone = os.getenv("SCW_DEFAULT_ZONE") or os.getenv("SCALEWAY_DEFAULT_ZONE", "fr-par-1")
    
    if not access_key or not secret_key or not project_id:
        error_msg = "Missing required Scaleway credentials"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Initializing Scaleway client with region={default_region}, zone={default_zone}")
    
    scaleway_client = Client(
        access_key=access_key,
        secret_key=secret_key,
        default_project_id=project_id,
        default_organization_id=organization_id,
        default_region=default_region,
        default_zone=default_zone,
    )
    
    return scaleway_client


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

async def list_instances_tool(zone: Optional[str] = None) -> str:
    """List all compute instances in a Scaleway zone."""
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Listing instances in zone: {target_zone}")
        
        response = instance_api.list_servers(zone=target_zone)
        instances = response.servers or []
        
        if not instances:
            return f"No instances found in zone {target_zone}."
        
        result = f"Found {len(instances)} instance(s) in zone {target_zone}:\n\n"
        for instance in instances:
            result += f"- **{instance.name}** (ID: {instance.id})\n"
            result += f"  - State: {instance.state}\n"
            result += f"  - Type: {instance.commercial_type}\n"
            result += f"  - Public IP: {instance.public_ip.address if instance.public_ip else 'None'}\n"
            result += f"  - Created: {instance.creation_date}\n\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to list instances: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


async def get_instance_tool(instance_id: str, zone: Optional[str] = None) -> str:
    """Get detailed information about a specific instance."""
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Getting instance {instance_id} in zone {target_zone}")
        
        response = instance_api.get_server(zone=target_zone, server_id=instance_id)
        instance = response.server
        
        result = f"**Instance Details: {instance.name}**\n\n"
        result += f"- ID: {instance.id}\n"
        result += f"- State: {instance.state}\n"
        result += f"- Type: {instance.commercial_type}\n"
        result += f"- Public IP: {instance.public_ip.address if instance.public_ip else 'None'}\n"
        result += f"- Private IP: {instance.private_ip or 'None'}\n"
        result += f"- Created: {instance.creation_date}\n"
        result += f"- Modified: {instance.modification_date}\n"
        
        if instance.volumes:
            result += f"- Volumes: {len(instance.volumes)}\n"
            for vol_id, volume in instance.volumes.items():
                result += f"  - {volume.name}: {volume.size}GB ({volume.volume_type})\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to get instance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


async def start_instance_tool(instance_id: str, zone: Optional[str] = None) -> str:
    """Start a stopped instance."""
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Starting instance {instance_id} in zone {target_zone}")
        
        instance_api.server_action(zone=target_zone, server_id=instance_id, action="poweron")
        
        return f"Successfully started instance {instance_id} in zone {target_zone}"
        
    except Exception as e:
        error_msg = f"Failed to start instance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


async def stop_instance_tool(instance_id: str, zone: Optional[str] = None) -> str:
    """Stop a running instance."""
    try:
        client = get_scaleway_client()
        instance_api = InstanceV1API(client)
        
        target_zone = zone or client.default_zone
        logger.info(f"Stopping instance {instance_id} in zone {target_zone}")
        
        instance_api.server_action(zone=target_zone, server_id=instance_id, action="poweroff")
        
        return f"Successfully stopped instance {instance_id} in zone {target_zone}"
        
    except Exception as e:
        error_msg = f"Failed to stop instance: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


async def list_k8s_clusters_tool(region: Optional[str] = None) -> str:
    """List all Kubernetes clusters in a Scaleway region."""
    try:
        client = get_scaleway_client()
        k8s_api = K8SV1API(client)
        
        target_region = region or client.default_region
        logger.info(f"Listing Kubernetes clusters in region: {target_region}")
        
        response = k8s_api.list_clusters(region=target_region)
        clusters = response.clusters or []
        
        if not clusters:
            return f"No Kubernetes clusters found in region {target_region}."
        
        result = f"Found {len(clusters)} Kubernetes cluster(s) in region {target_region}:\n\n"
        for cluster in clusters:
            result += f"- **{cluster.name}** (ID: {cluster.id})\n"
            result += f"  - Status: {cluster.status}\n"
            result += f"  - Version: {cluster.version}\n"
            result += f"  - CNI: {cluster.cni}\n\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to list Kubernetes clusters: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


# Tool registry mapping tool names to implementations
TOOL_REGISTRY = {
    "list_instances": list_instances_tool,
    "get_instance": get_instance_tool,
    "start_instance": start_instance_tool,
    "stop_instance": stop_instance_tool,
    "list_k8s_clusters": list_k8s_clusters_tool,
}


# ============================================================================
# MCP SERVER SETUP
# ============================================================================

# Global handler functions
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="list_instances",
                description="List all compute instances in a Scaleway zone",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "zone": {
                            "type": "string",
                            "description": "Scaleway zone (e.g., fr-par-1, nl-ams-1). Optional, uses default if not provided."
                        }
                    }
                }
            ),
            Tool(
                name="get_instance",
                description="Get detailed information about a specific instance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "The ID of the instance to retrieve"
                        },
                        "zone": {
                            "type": "string",
                            "description": "Scaleway zone. Optional, uses default if not provided."
                        }
                    },
                    "required": ["instance_id"]
                }
            ),
            Tool(
                name="start_instance",
                description="Start a stopped instance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "The ID of the instance to start"
                        },
                        "zone": {
                            "type": "string",
                            "description": "Scaleway zone. Optional, uses default if not provided."
                        }
                    },
                    "required": ["instance_id"]
                }
            ),
            Tool(
                name="stop_instance",
                description="Stop a running instance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "The ID of the instance to stop"
                        },
                        "zone": {
                            "type": "string",
                            "description": "Scaleway zone. Optional, uses default if not provided."
                        }
                    },
                    "required": ["instance_id"]
                }
            ),
            Tool(
                name="list_k8s_clusters",
                description="List all Kubernetes clusters in a Scaleway region",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "Scaleway region (e.g., fr-par, nl-ams). Optional, uses default if not provided."
                        }
                    }
                }
            ),
        ]
    )

async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Execute a tool."""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")
    
    tool_func = TOOL_REGISTRY[name]
    result_text = await tool_func(**arguments)
    
    return CallToolResult(
        content=[TextContent(type="text", text=result_text)]
    )

def create_mcp_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("scaleway")
    
    @server.list_tools()
    async def _list_tools() -> ListToolsResult:
        return await list_tools()
    
    @server.call_tool()
    async def _call_tool(name: str, arguments: dict) -> CallToolResult:
        return await call_tool(name=name, arguments=arguments)
    
    return server


# ============================================================================
# FASTAPI HTTP SERVER
# ============================================================================

app = FastAPI(title="Scaleway MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "Scaleway MCP Server",
        "version": "1.0.0",
        "protocol": "MCP",
        "transport": "HTTP"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/mcp")
async def mcp_post(request: Request):
    """Handle MCP POST requests (client-to-server messages)."""
    try:
        body = await request.json()
        logger.info(f"Received MCP message: {body.get('method', 'unknown')}")
        
        # Handle different JSON-RPC methods
        method = body.get("method")
        
        if method == "initialize":
            # Return initialization response
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "scaleway",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif method == "tools/list":
            # List available tools - call the handler function directly
            tools_result = await list_tools()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        }
                        for tool in tools_result.tools
                    ]
                }
            })
        
        elif method == "tools/call":
            # Call a tool
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            result = await call_tool(name=tool_name, arguments=arguments)
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [
                        {
                            "type": content.type,
                            "text": content.text
                        }
                        for content in result.content
                    ]
                }
            })
        
        elif method == "notifications/initialized":
            # Handle initialization notification (no response needed for notifications)
            logger.info("Client initialization notification received")
            return JSONResponse({
                "jsonrpc": "2.0"
            })
        
        elif method.startswith("notifications/"):
            # Handle other notifications (no response needed)
            logger.info(f"Notification received: {method}")
            return JSONResponse({
                "jsonrpc": "2.0"
            })
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {method}")
    
    except Exception as e:
        logger.error(f"Error handling MCP request: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if "body" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
        )


if __name__ == "__main__":
    # Initialize the Scaleway client on startup
    try:
        get_scaleway_client()
        logger.info("Scaleway client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Scaleway client: {e}")
        sys.exit(1)
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    
    logger.info(f"Starting Scaleway MCP HTTP server on {host}:{port}")
    
    # Run the server
    uvicorn.run(app, host=host, port=port, log_level="info")
